[Setup]
AppName=Late4Bus
AppVersion=1.0.0
AppPublisher=Dexter Wong
DefaultDirName={autopf}\Late4Bus
DefaultGroupName=Late4Bus
OutputBaseFilename=Late4Bus_Setup_v1.0.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "dist\Late4Bus.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Late4Bus"; Filename: "{app}\Late4Bus.exe"
Name: "{commondesktop}\Late4Bus"; Filename: "{app}\Late4Bus.exe"

[Run]
Filename: "{app}\Late4Bus.exe"; Description: "Launch Late4Bus"; Flags: nowait postinstall skipifsilent