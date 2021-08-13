; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "Beskar"
#define MyAppVersion "v1.1.1"
#define MyAppPublisher "Ahsoka"
#define MyAppExeName "Beskar.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{81765D16-4975-4971-8191-13E67595DC19}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
; Is actually support link not app publisher link
AppPublisherURL="https://github.com/Ahsoka"
AppSupportURL="https://github.com/Ahsoka/beskar/issues"
AppUpdatesURL="https://github.com/Ahsoka/beskar/releases/latest"
DefaultDirName={autopf64}\{#MyAppName}
DisableProgramGroupPage=yes
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=commandline dialog
OutputDir={#SourcePath}
OutputBaseFilename=beskar-install-v1.1.1-64bit
SetupIconFile=dist\Beskar\images\beskar-icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
LicenseFile=LICENSE

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\Beskar\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Beskar\certifi\cacert.pem"; DestDir: "{app}\certifi"; Flags: ignoreversion
Source: "dist\Beskar\*"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Beskar\qss\*"; DestDir: "{app}\qss"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\Beskar\fonts\*"; DestDir: "{app}\fonts"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\Beskar\desc\*"; DestDir: "{app}\desc"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\Beskar\images\*"; DestDir: "{app}\images"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\Beskar\numpy\*"; DestDir: "{app}\numpy"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\Beskar\platforms\*"; DestDir: "{app}\platforms"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\Beskar\PyQt6\*"; DestDir: "{app}\PyQt6"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\Beskar\styles\*"; DestDir: "{app}\styles"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\images\beskar-icon.ico"; AppUserModelID: "Ahsoka.Beskar.main.{#MyAppVersion}"
Name: "{userprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\images\beskar-icon.ico"; AppUserModelID: "Ahsoka.Beskar.main.{#MyAppVersion}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\images\beskar-icon.ico"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
