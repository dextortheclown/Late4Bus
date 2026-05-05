[Setup]
AppName=Late4Bus
AppVersion=1.2.1
AppPublisher=Dexter Wong
AppPublisherURL=https://github.com/dextortheclown/late4bus
AppSupportURL=https://github.com/dextortheclown/late4bus/issues
AppUpdatesURL=https://github.com/dextortheclown/late4bus/releases
DefaultDirName={autopf}\Late4Bus
DefaultGroupName=Late4Bus
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=Late4Bus_Setup_v1.2.1
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked
Name: "startupicon"; Description: "Launch Late4Bus when Windows starts"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "dist\Late4Bus.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
Name: "{group}\Late4Bus"; Filename: "{app}\Late4Bus.exe"; IconFilename: "{app}\icon.ico"
Name: "{group}\Uninstall Late4Bus"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Late4Bus"; Filename: "{app}\Late4Bus.exe"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "Late4Bus"; ValueData: """{app}\Late4Bus.exe"""; Flags: uninsdeletevalue; Tasks: startupicon

[Run]
Filename: "{app}\Late4Bus.exe"; Description: "Launch Late4Bus now"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
Type: filesandordirs; Name: "{userappdata}\Late4Bus"