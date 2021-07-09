; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "Beskar"
#define MyAppVersion "v0.7.0-beta"
#define MyAppPublisher "Ahsoka"
#define MyAppURL "https://github.com/Ahsoka/beskar"
#define MyAppExeName "Beskar.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{81765D16-4975-4971-8191-13E67595DC19}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=commandline
OutputDir=C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)
OutputBaseFilename=beskar-install-v0.7.0-beta-64bit
SetupIconFile=C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\images\beskar-icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
LicenseFile=C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\LICENSE

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\_asyncio.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\_bz2.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\_ctypes.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\_decimal.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\_hashlib.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\_lzma.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\_multiprocessing.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\_overlapped.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\_queue.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\_socket.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\_ssl.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-console-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-datetime-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-debug-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-errorhandling-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-file-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-file-l1-2-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-file-l2-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-handle-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-heap-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-interlocked-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-libraryloader-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-localization-l1-2-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-memory-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-namedpipe-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-processenvironment-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-processthreads-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-processthreads-l1-1-1.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-profile-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-rtlsupport-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-string-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-synch-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-synch-l1-2-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-sysinfo-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-timezone-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-core-util-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-crt-conio-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-crt-convert-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-crt-environment-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-crt-filesystem-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-crt-heap-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-crt-locale-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-crt-math-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-crt-process-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-crt-runtime-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-crt-stdio-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-crt-string-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-crt-time-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\api-ms-win-crt-utility-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\base_library.zip"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\Beskar.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\Beskar.exe.manifest"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\libcrypto-1_1-x64.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\libffi-7.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\libopenblas.GK7GX5KEQ4F6UYO3P26ULGBQYHGQO7J4.gfortran-win_amd64.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\libssl-1_1-x64.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\MSVCP140.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\MSVCP140_1.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\pyexpat.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\python3.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\python38.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\Qt6Charts.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\Qt6Core.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\Qt6DataVisualization.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\Qt6Gui.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\Qt6OpenGL.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\Qt6OpenGLWidgets.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\Qt6PrintSupport.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\Qt6Test.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\Qt6Widgets.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\select.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\ucrtbase.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\unicodedata.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\VCRUNTIME140.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\VCRUNTIME140_1.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\images\*"; DestDir: "{app}\images"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\numpy\*"; DestDir: "{app}\numpy"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\platforms\*"; DestDir: "{app}\platforms"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\PyQt6\*"; DestDir: "{app}\PyQt6"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\AA12 Louqe\Google Drive\Coding\Github Repositories\Beskar (Solar Army)\dist\Beskar\styles\*"; DestDir: "{app}\styles"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\images\beskar-icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\images\beskar-icon.ico"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
