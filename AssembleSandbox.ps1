Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
# StartUp
# Elements
# Custom Config
# Systems
# Modules
# GM Console

function Create-Form {
    param(
        [string]$FormTitle,
        [string[]]$Options
    )

    $form = New-Object System.Windows.Forms.Form
    $form.Text = $FormTitle
    $form.Size = New-Object System.Drawing.Size(300,200)
    $form.StartPosition = 'CenterScreen'

    $OKButton = New-Object System.Windows.Forms.Button
    $OKButton.Location = New-Object System.Drawing.Point(75,120)
    $OKButton.Size = New-Object System.Drawing.Size(75,23)
    $OKButton.Text = 'OK'
    $OKButton.DialogResult = [System.Windows.Forms.DialogResult]::OK
    $form.AcceptButton = $OKButton
    $form.Controls.Add($OKButton)

    $CancelButton = New-Object System.Windows.Forms.Button
    $CancelButton.Location = New-Object System.Drawing.Point(150,120)
    $CancelButton.Size = New-Object System.Drawing.Size(75,23)
    $CancelButton.Text = 'Cancel'
    $CancelButton.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
    $form.CancelButton = $CancelButton
    $form.Controls.Add($CancelButton)

    $label = New-Object System.Windows.Forms.Label
    $label.Location = New-Object System.Drawing.Point(10,20)
    $label.Size = New-Object System.Drawing.Size(280,20)
    $label.Text = 'Please make a selection from the list below:'
    $form.Controls.Add($label)

    $listBox = New-Object System.Windows.Forms.Listbox
    $listBox.Location = New-Object System.Drawing.Point(10,40)
    $listBox.Size = New-Object System.Drawing.Size(260,20)

    $listBox.SelectionMode = 'MultiExtended'

    Foreach ($option IN $Options) {
        [void] $listBox.Items.Add($option)

    }
    $listBox.Height = 70
    $form.Controls.Add($listBox)
    $form.Topmost = $true

    $result = $form.ShowDialog()
    if ($result -eq [System.Windows.Forms.DialogResult]::OK)
    {
        return $listBox.SelectedItems
    }
    return @()
}

function Find-StartIndex {
    param(
        [string[]]$Data
    )

    for($i=0; $i -lt $Data.length; $i++) {
        if ($Data[$i].contains("</start>")) {
            return $i+1
        }
    }
}

New-Item -ItemType File -Path "MISS_TSN-Command.xml" -Force

$start = Get-Content -Path "XML Files/Start Up.xml"
$elems = Get-Content -Path "XML Files/Elements.xml"
$cuco = Get-Content -Path "XML Files/Custom Config.xml"
$gmco = Get-Content -Path "XML Files/GM Console.xml"

$systems = (Get-ChildItem -Path "XML Files/Star Systems" -File -Filter "*.xml").Name
$modules = (Get-ChildItem -Path "XML Files/Custom Scripts" -File -Filter "*.xml").Name

$selectedSystems = Create-Form -FormTitle "System Select" -Options $systems
$selectedModules = Create-Form -FormTitle "Module Select" -Options $modules

$data = $start[0..($start.count-2)]
$data = $data + $elems[4..($elems.count-2)]
$data = $data + $cuco[8..($cuco.count-2)]

Foreach ($system IN $selectedSystems) {
    Write-Host $system
    $sys = Get-Content -Path ("XML Files/Star Systems/" + $system)
    $data = $data + $sys[6..($sys.count-2)]
}

Foreach ($module IN $selectedModules) {
    Write-Host $module
    Write-Host (Find-StartIndex -Data $sys)
    $sys = Get-Content -Path ("XML Files/Custom Scripts/" + $module)
    $data = $data + $sys[(Find-StartIndex -Data $sys)..($sys.count-2)]
}

$data = $data + $gmco[4..($gmco.count-2)]
$data = $data + $start[($start.count-1)]

$data | Out-File "MISS_TSN-Command.xml" -Encoding ASCII