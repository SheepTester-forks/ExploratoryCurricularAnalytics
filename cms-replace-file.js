/**
 * @file browser script (copypaste and run in console) that adds a file input to
 * every entry on UCSD's CMS that allows me to upload a large HTML file to
 * overwrite an existing file.
 *
 * Run in the CMS folder view to replace HTML reports.
 *
 * ::web
 */

async function writeFile (fileId, contents, message) {
  const submittedFormIdentifier = (
    await fetch(`/entity/edit.act?id=${fileId}&type=file`).then(r => r.text())
  ).match(
    /<input type="hidden" name="submittedFormIdentifier" value="([0-9a-z]+)"\/>/
  )[1]

  let formData = new FormData()
  formData.set('submittedFormIdentifier', submittedFormIdentifier)
  formData.set('id', fileId)
  formData.set('bytesAsString', contents)
  formData.set('shouldBeIndexed', 'on')
  formData.set('shouldBePublished', 'on')
  formData.set('customLinkRewriting', 'ABSOLUTE')

  await fetch('/entity/submitfile.act?saveAs=draft', {
    body: formData,
    method: 'POST'
  })

  const submitId = (
    await fetch(`/entity/open.act?type=file&id=${fileId}`).then(r => r.text())
  ).match(/<input type="hidden" name="id" value="([0-9a-z]+)"\/>/)[1]

  formData = new FormData()
  formData.set('type', 'file')
  formData.set('id', submitId)
  formData.set('dataCheckSettings.comments', message)

  await fetch('/entity/submitDraft.act?submitButtonType=submit', {
    method: 'POST',
    body: formData
  })
}

for (const assetRow of document.querySelectorAll(
  '#DataTables_Table_0_wrapper td:nth-child(2)'
)) {
  const assetId = new URL(assetRow.children[0].href).searchParams.get('id')
  const label = document.createElement('label')
  const fileInput = Object.assign(document.createElement('input'), {
    type: 'file'
  })
  label.append('Replace file: ', fileInput)
  assetRow.append(label)

  fileInput.addEventListener('change', async () => {
    if (fileInput.files[0]) {
      fileInput.disabled = true
      await writeFile(
        assetId,
        await fileInput.files[0].text(),
        prompt('Change message')
      )
      fileInput.value = ''
      fileInput.disabled = false
    }
  })
}
