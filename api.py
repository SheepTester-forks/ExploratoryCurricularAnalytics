"""
Defines helper methods that interface directly with Curricular Analytics'
internal API. Think of it like discord.js but for Curricular Analytics.

::ca::main
"""

from http.client import HTTPResponse
import json
import re
from typing import (
    Any,
    Dict,
    List,
    Literal,
    NamedTuple,
    Optional,
    Tuple,
    Union,
)
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from output_json import (
    Curriculum,
    VisCurriculum,
    VisUpdateCurriculum,
    DegreePlan,
    VisDegreePlan,
    VisUpdateDegreePlan,
)

CsvFile = Tuple[str, str]
FormData = Dict[str, Union[str, Tuple[str, bytes]]]


class UrlOpenReturn(HTTPResponse):
    """
    HACK: Mimic urllib.request.urlopen's return type. Their docs say they return
    a `HTTPResponse`, but that doesn't have a `url` attribute, and I don't know
    how to do intersections in Python typing.
    """

    url: str


class Blob(bytearray):
    def write_line(self, line: Union[str, bytes] = "") -> None:
        if type(line) is str:
            self.extend(line.encode("utf-8"))
        elif type(line) is bytes:
            self.extend(line)
        self.extend(b"\r\n")


HOST = "https://curricularanalytics.org"


class CurriculumEntry(NamedTuple):
    """
    A row in the table listing the user's curricula on Curricular Analytics.
    """

    raw_name: str
    raw_organization: str
    cip_code: str
    year: int
    date_created: str

    def curriculum_id(self) -> int:
        """
        Get the ID of the curriculum from its URL in the "Name" column
        (`raw_name`).
        """
        match = re.match(r'<a href="/curriculums/(\d+)', self.raw_name)
        if match is None:
            raise ValueError(
                f"The name of the curriculum entry `{self.raw_name}` doesn't seem to be a link."
            )
        return int(match.group(1))


class Session:
    session: str
    # Same as CSRF token, as it turns out
    authenticity_token: Optional[str]

    def __init__(self, session: str, authenticity_token: Optional[str] = None) -> None:
        """
        `authenticity_token` is optional because it can get one by itself, but
        you can help save a request by providing your own.
        """
        self.session = session
        self.authenticity_token = authenticity_token

    def request(
        self,
        path: str,
        headers: Dict[str, str] = {},
        data: Optional[bytes] = None,
        method: str = "GET",
    ) -> UrlOpenReturn:
        try:
            return urlopen(
                Request(
                    HOST + path,
                    headers={
                        **headers,
                        "Cookie": f"_curricularanalytics_session={self.session}",
                    },
                    data=data,
                    method=method,
                )
            )
        except HTTPError as error:
            raise RuntimeError(
                "Curricular Analytics isn't recognizing your `CA_SESSION` environment variable. Could you try getting the session cookie again? See the README for how."
            ) if error.code == 401 else error

    def get_json(self, path: str) -> Any:
        with self.request(path, {"Accept": "application/json"}) as response:
            return json.load(response)

    def get_auth_token(self) -> str:
        if self.authenticity_token is None:
            with self.request("/degree_plans") as response:
                match = re.search(
                    rb'<meta name="csrf-token" content="([\w+=/]+)" />',
                    response.read(),
                )
                if match is None:
                    raise RuntimeError(
                        "Could not get `authenticity_token` from a form."
                    )
                token = match.group(1).decode("utf-8")
                self.authenticity_token = token
                return token
        else:
            return self.authenticity_token

    BOUNDARY = "BOUNDARY"

    def post_form(
        self,
        path: str,
        form: FormData,
    ) -> None:
        """
        Submits an HTML form on Curricular Analytics with a POST request. The
        request body is `multipart/form-data`, so it can contain files.

        `url` is the URL that the form posts to (NOT the URL of the page that the
        form is on). `form` contains a dictionary mapping field names (i.e. the
        `name` attribute of the `<input />` elements) to string values or a tuple
        with a file name and the contents of the file.

        Handles authentication (includes the `Cookie` header based on the
        `CA_SESSION` environment variable) and identifies and raises errors for when
        the session or form's authenticity token are invalid.
        """
        if all(type(value) is str for value in form.values()):
            request = self.request(
                path,
                {"Content-Type": "application/x-www-form-urlencoded"},
                urlencode(
                    {
                        name: value if type(value) is str else ""
                        for name, value in form.items()
                    }
                ).encode("utf-8"),
                "POST",
            )
        else:
            body: Blob = Blob()
            for name, value in form.items():
                body.write_line(f"--{Session.BOUNDARY}")
                if type(value) is str:
                    body.write_line(f'Content-Disposition: form-data; name="{name}"')
                    body.write_line()
                    body.write_line(value)
                elif type(value) is tuple:
                    file_name, content = value
                    body.write_line(
                        f'Content-Disposition: form-data; name="{name}"; filename="{file_name}"'
                    )
                    body.write_line("Content-Type: application/octet-stream")
                    body.write_line()
                    body.write_line(content)
            body.write_line(f"--{Session.BOUNDARY}--")
            request = self.request(
                path,
                {"Content-Type": f"multipart/form-data; boundary={Session.BOUNDARY}"},
                body,
                "POST",
            )
        with request as response:
            if response.url == HOST + "/users/sign_in":
                raise RuntimeError(
                    "Curricular Analytics isn't recognizing your `CA_SESSION` environment variable. Could you try getting the session cookie again? See the README for how."
                )

    def upload_curriculum(
        self,
        organization_id: int,
        name: str,
        year: int,
        data: Union[CsvFile, Curriculum],
        cip_code: str = "",
    ) -> None:
        """
        Creates a new curriculum under the given organization.
        """
        form: FormData
        if isinstance(data, tuple):
            file_name, csv = data
            form = {
                "curriculum[curriculum_file]": (file_name, csv.encode("utf-8")),
                "entry_method": "csv_file",
            }
        else:
            form = {
                "entry_method": "gui",
                "curriculum_json": json.dumps(data),
            }
        self.post_form(
            "/curriculums",
            {
                "authenticity_token": self.get_auth_token(),
                "curriculum[name]": name,
                "curriculum[organization_id]": str(organization_id),
                "curriculum[catalog_year]": str(year),
                "curriculum[cip]": cip_code,  # Curricular Analytics will get it from the CSV
                **form,
            },
        )

    def upload_degree_plan(
        self, curriculum_id: int, name: str, data: Union[CsvFile, Curriculum]
    ) -> None:
        """
        Creates a new degree plan under the given curriculum.
        """
        form: FormData
        if isinstance(data, tuple):
            file_name, csv = data
            form = {
                "degree_plan[degree_plan_file]": (file_name, csv.encode("utf-8")),
                "entry_method": "csv_file",
            }
        else:
            form = {
                "entry_method": "gui",
                "curriculum_json": json.dumps(data),
            }
        self.post_form(
            "/degree_plans",
            {
                "authenticity_token": self.get_auth_token(),
                "degree_plan[name]": name,
                "degree_plan[curriculum_id]": str(curriculum_id),
                **form,
            },
        )

    def get_curricula(
        self,
        sort_by: int,
        direction: Literal["desc", "asc"] = "asc",
        offset: int = 0,
        items: int = 1,
        search: str = "",
    ) -> List[CurriculumEntry]:
        """
        Get the user's curricula on Curricular Analytics. This is equivalent to the
        table the user sees at https://curricularanalytics.org/curriculums.

        Used by `upload_major` to get the ID of the most recently created
        curriculum.

        `sort_by` should be the index of the column to sort by, and `direction` is
        whether it should be sorted in ascending (`asc`) or descending (`desc`)
        order. For example, to get the most recent curricula, the creation date is
        the fifth column (index 4), and to put the latest date first, sort it in
        descending order.

        ```py
        curricula = get_curricula(4, 'desc')
        ```

        `offset` is the index into the results to start returning curricula, while
        `items` is the maximum number of curricula to get. `search` filters the list
        of curricula by a keyword.
        """
        params = urlencode(
            {
                "order[0][column]": sort_by,
                "order[0][dir]": direction,
                "start": offset,
                "length": items,
                "search[value]": search,
            }
        )
        data = self.get_json("/curriculums?" + params)["data"]
        return [
            CurriculumEntry(raw_name, raw_organization, cip_code, year, date_created)
            for raw_name, raw_organization, cip_code, year, date_created, _ in data
        ]

    def get_degree_plans(self, curriculum_id: int) -> Dict[str, int]:
        with self.request(f"/curriculums/{curriculum_id}") as response:
            return {
                match.group(2): int(match.group(1))
                for match in re.finditer(
                    r'<a href="/degree_plans/(\d+)">([^<]+)</a>',
                    response.read().decode("utf-8"),
                )
            }

    def get_curriculum(self, curriculum_id: int) -> VisCurriculum:
        return self.get_json(f"/vis_curriculum_hash/{curriculum_id}")

    def get_degree_plan(self, plan_id: int) -> VisDegreePlan:
        return self.get_json(f"/vis_degree_plan_hash/{plan_id}")

    def edit_curriculum(self, curriculum_id: int, curriculum: Curriculum) -> None:
        with self.request(
            f"/curriculums/viz_update/{curriculum_id}",
            {"Content-Type": "application/json", "X-CSRF-Token": self.get_auth_token()},
            json.dumps(VisUpdateCurriculum(curriculum=curriculum)).encode("utf-8"),
            "PATCH",
        ):
            pass

    def edit_curriculum_metadata(
        self,
        curriculum_id: int,
        name: Optional[str] = None,
        cip_code: Optional[str] = None,
        organization_id: Optional[int] = None,
        year: Optional[int] = None,
        public: Optional[bool] = None,
    ) -> None:
        form: FormData = {
            "authenticity_token": self.get_auth_token(),
            "_method": "patch",
        }
        if name is not None:
            form["curriculum[name]"] = name
        if cip_code is not None:
            form["curriculum[cip]"] = cip_code
        if organization_id is not None:
            form["curriculum[organization_id]"] = str(organization_id)
        if year is not None:
            form["curriculum[catalog_year]"] = str(year)
        if public is not None:
            form["curriculum[publicly_visible]"] = str(int(public))
        self.post_form(f"/curriculums/{curriculum_id}", form)

    def edit_degree_plan(self, plan_id: int, curriculum: Curriculum) -> None:
        with self.request(
            f"/degree_plans/viz_update/{plan_id}",
            {"Content-Type": "application/json", "X-CSRF-Token": self.get_auth_token()},
            json.dumps(
                VisUpdateDegreePlan(
                    curriculum=curriculum, degree_plan=DegreePlan(id=plan_id)
                )
            ).encode("utf-8"),
            "PATCH",
        ):
            pass

    def destroy_curriculum(self, curriculum_id: int) -> None:
        self.post_form(
            f"/curriculums/{curriculum_id}",
            {
                "authenticity_token": self.get_auth_token(),
                "_method": "delete",
            },
        )

    def destroy_degree_plan(self, plan_id: int) -> None:
        self.post_form(
            f"/degree_plans/{plan_id}",
            {
                "authenticity_token": self.get_auth_token(),
                "_method": "delete",
            },
        )


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
    ca_session = os.getenv("CA_SESSION")
    if ca_session is None:
        raise EnvironmentError("No CA_SESSION environment variable")
    session = Session(ca_session)

    session.edit_curriculum_metadata(20069, public=True, name="very cool")
