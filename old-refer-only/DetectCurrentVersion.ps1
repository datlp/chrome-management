$OS = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion"
PS C:\Users\Dat> [PSCustomObject]@ {
    >>     Name           = $OS.ProductName
    >>     DisplayVersion = $OS.DisplayVersion
    >>     CurrentBuild   = $OS.CurrentBuild
    >>     UBR            = $OS.UBR # Update Build Revision
    >> }

Name           DisplayVersion CurrentBuild  UBR
----           -------------- ------------  -- -
Windows 10 Pro 23H2           22631        6199