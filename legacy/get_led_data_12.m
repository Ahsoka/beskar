function [stat_out]=get_led_data_10()
%
%   Syntax:
%       [dat_out,dat_mat]=get_led_data_7();
%
%   Program to control led pulsers and read out
%   photocurrents
%
%
%
warning off;
mult=-1;    %anodic for plotting; will change if applied voltage < 0
voffset=2.5;    %estimated voltage offset
%
%
dat_out=[];
dat_mat=[];
stat_out=-1;
%
%
close all;
init_message=['Looking for Installed Adaptors'];
h = msgbox(init_message,'Startup','replace');
%
a=daqhwinfo();
%
%
aok=sum(strcmp(a.InstalledAdaptors,'nidaq'));
%
if aok > 0
    tst=a.InstalledAdaptors;
    [asz,bsz]=size(tst);
    for LL1=1:asz
        if  strcmp(tst(LL1),'nidaq')
            ANIDAQ=LL1;
        end
    end
else
%    aok <= 0
    IA_str=char(a.InstalledAdaptors);
    [IA_str_a,IA_str_b]=size(IA_str);
    close all;
    error_message={'nidaq adsator not found'; '  '; 'Installed adaptors:'; '  '; char(a.InstalledAdaptors)};
    h = errordlg(error_message,'Startup','modal');
    pause(5)
    return
end
%
init_message=['Found: ',char(tst(ANIDAQ))];
h = msgbox(init_message,'Startup','replace');
%
%   Get Device ID #
%
init_message=['Getting NI Device ID'];
h = msgbox(init_message,'Startup','replace');
%
a=daqhwinfo('nidaq');
Dev_ID=char(a.InstalledBoardIds);
%
if isempty(Dev_ID)
    close all;
    error_message={'NI device not installed';'  ';'Make sure USB cable is connected';'  ';'Run Program as Administrator'};
    h = errordlg(error_message,'Startup','modal');
    pause(5)
    return
end
%
init_message=['NI Device ID:',Dev_ID];
h = msgbox(init_message,'Startup','replace');
%
%
%       Configure Analog Input
%
init_message=['Configuring Analog Input'];
h = msgbox(init_message,'Startup','replace');
%
AI = analoginput('nidaq',Dev_ID);
AICH = addchannel(AI,0);
%AIchans1=AI.Channel
set(AI,'InputType','Differential');
AI.Channel.Units='Volts';
AI.Channel.InputRange=[-10 10];
set(AI,'Timeout',70);
set(AI,'TriggerType','HwDigital');
set(AI,'HwDigitalTriggerSource','PFI0');
set(AI,'TriggerCondition','NegativeEdge');
set(AI,'SampleRate',5);
set(AI,'SamplesPerTrigger',2);
set(AI,'TriggerRepeat',64);
set(AI,'SamplesAcquiredFcnCount',130);
%
%       Configure Analog Output
%
init_message=['Configuring Analog Output'];
h = msgbox(init_message,'Startup','replace');
%
AO = analogoutput('nidaq',Dev_ID);
AOCH = addchannel(AO,0);
set(AO,'TriggerType','Immediate');
set(AOCH,'UnitsRange',[0 5])
AO_dat=0;
AO_dat_set=AO_dat+voffset;
putsample(AO,AO_dat_set);
wait(AO,2);
%
close(h);
%

%
%   voltage calibration routine
%
voff_corr_str=inputdlg('Enter the DVM Reading in VOLTS:','Voltage Calibration',1,{'0'});
if isempty(voff_corr_str)
    voff_corr_str={'0'};
end
voff_corr=str2num(char(voff_corr_str));
voffset=voffset+voff_corr;
%
AO_dat=0;
AO_dat_set=AO_dat+voffset;
putsample(AO,AO_dat_set);
wait(AO,2);
%
appV_prompt={'Enter the voltage to apply (-5 < Volts < 5)'};
appV_dlg_title='Applied Voltage';
appV_num_lines=1;
appV_def={'0'};
AO_dat_app=0;
%
%
%       Configure DIO
%
init_message=['Reading Hardware Versions'];
h = msgbox(init_message,'Startup','replace');
%
DIO = digitalio('nidaq',Dev_ID);
DIOlines = addline(DIO,0:11,'in');
%
versions=getvalue(DIO);
%
INT_ver=binvec2dec(versions(5:8));
LED_ver=binvec2dec(versions(9:12));
%
init_message={['LED Hardware Version: ',num2str(LED_ver)]; ['Integrator Hardware Version: ',num2str(INT_ver)]};
h = msgbox(init_message,'Startup','replace');
%
pause(2)
%close(h);
%LED_SER_NO=-1;
%options.Resize='on';
%options.WindowStyle='modal';
%options.Interpreter='none';
%dlg_prompt='Enter Number on LED label:';
%dlg_title='LED SERIAL NUMBER';
%def_ans={' '};
%while LED_SER_NO <= 0   % check serial number to determine number of triggers to collect.
%    LED_SER_NO_str=inputdlg(dlg_prompt,dlg_title,1,def_ans,options);
%    if isempty(LED_SER_NO_str)
%        LED_SER_NO=-1;
%    elseif ~isempty(str2num(char(LED_SER_NO_str)));
%        LED_SER_NO=str2num(char(LED_SER_NO_str));
%    end
%end
%
%
ITR=64;     %total # of triggers = ITR+1
LED_SER=1;
%
if LED_ver == 1     % LED flasher design, SCH ver 1.2; PCB ver 2.1.3
%
%     transL left multiplies data matrix to interchange rows
%
    transL = [
        0     0     0     0     0     0     1     0
        0     1     0     0     0     0     0     0
        0     0     0     0     1     0     0     0
        0     0     0     1     0     0     0     0
        0     0     1     0     0     0     0     0
        0     0     0     0     0     1     0     0
        1     0     0     0     0     0     0     0
        0     0     0     0     0     0     0     1];    
%
%     transR right multiplies data matrix to interchange columns
%
    transR = [
        0     0     0     1     0     0     0     0;
        0     0     0     0     0     0     0     1;
        0     1     0     0     0     0     0     0;
        0     0     0     0     0     1     0     0;
        0     0     0     0     0     0     1     0;
        0     0     1     0     0     0     0     0;
        0     0     0     0     1     0     0     0;
        1     0     0     0     0     0     0     0];
else
%
%     transL left multiplies data matrix to interchange rows
%
    transL = [
        0     0     0     0     0     0     0     1;
        1     0     0     0     0     0     0     0;
        0     0     0     0     0     1     0     0;
        0     0     1     0     0     0     0     0;
        0     0     0     1     0     0     0     0;
        0     0     0     0     1     0     0     0;
        0     1     0     0     0     0     0     0;
        0     0     0     0     0     0     1     0];
%
%     transR right multiplies data matrix to interchange columns
%
    transR = [
        0     0     0     1     0     0     0     0;
        0     0     0     0     0     0     0     1;
        0     1     0     0     0     0     0     0;
        0     0     0     0     0     1     0     0;
        0     0     0     0     0     0     1     0;
        0     0     1     0     0     0     0     0;
        0     0     0     0     1     0     0     0;
        1     0     0     0     0     0     0     0];
%
end
%
pause(5);
%
% clear digital input lines
%
delete(DIO);
%
init_message=['Configuring Digital Output'];
h = msgbox(init_message,'Startup','replace');
%
DIO = digitalio('nidaq',Dev_ID);
DIOlines = addline(DIO,0:7,'out');
dio_dat_low=0;                  
dio_dat_hi=1;                  
putvalue(DIO,dio_dat_hi);      %Set line 0 hi to inhibit pulsing
%
%
pause(0.5);
putvalue(DIO,dio_dat_low);      %Set DIO line 0 low to start pulsing
pause(0.1);
putvalue(DIO,dio_dat_hi);      %Set DIO line 0 hi to stop pulsing   
%
close(h);
%    
x=0;
cntdwn=-60;
close all;
h = waitbar(x,'LED Initialization');
while cntdwn > 0
%    init_message=['Initialization time remaining: ~',num2str(cntdwn),' seconds'];
%    h = waitbar(x,'LED Initialization');
%    h = msgbox(init_message,'LED Initialization','replace');
%    if cntdwn == 60
%        pause(4);
%        cntdwn=cntdwn-4;
%        x=1-(cntdwn./64);
%    else
    pause(5);
    cntdwn=cntdwn-5;
    x=1-(cntdwn./60);
%    end
    h = waitbar(x,h);
%    close(h);
end
if ishandle(h);
    close(h);
end
%
%
%
%   Configure scan parameters
%
scan_prompt={'Enter the number of cycles to average'};
scan_title='Scan Cycles';
scan_num_lines=1;
scan_def={'1'};
%
%
%
%
choice= 0;
while choice < 9
choice = menu('Select an Option','Re-Initialize LED Array','Apply Voltage','Turn off Voltage','Check Dark Current','Perform an LED Scan','Save LED Data to a File','Perform an I/V Scan','Go to Solar Materials Discovery Website','Exit Program');
%
if choice == 1
    pause(0.5);
    putvalue(DIO,dio_dat_low);      %Set DIO line 0 low to start pulsing
    pause(0.1);
    putvalue(DIO,dio_dat_hi);      %Set DIO line 0 hi to stop pulsing   
%    
    x=0;
    cntdwn=60;
    close all;
    h = waitbar(x,'LED Initialization');
    while cntdwn > 0
%        init_message=['Time remaining: ~',num2str(cntdwn),' seconds'];
%        h = msgbox(init_message,'Initializing','replace');
%        if cntdwn == 64
%            pause(4);
%            cntdwn=cntdwn-4;
%            x=1-(cntdwn./64);
%        else
        pause(5);
        cntdwn=cntdwn-5;
        x=1-(cntdwn./60);
        h = waitbar(x,h);
    end
    if ishandle(h);
        close(h);
    end
    %
elseif choice == 2
%
    AO_ans=inputdlg(appV_prompt,appV_dlg_title,appV_num_lines,appV_def);
    if ~isempty(AO_ans)
        AO_dat=str2num(char(AO_ans));
%
        if AO_dat >= 0  % anodic
            mult = -1;
        else            % cathodic
            mult = 1;
        end
%
        AO_dat=-AO_dat;
%
        if AO_dat > 5
            AO_dat =5;
        elseif AO_dat < -5
            AO_dat=-5;
        end
        delt=AO_dat-AO_dat_app;
        LP=fix(abs(delt./0.1));
        if delt < 0
            vinc = -0.1;
        elseif delt > 0
            vinc = 0.1;
        else
            vinc = 0;
        end
        AO_dat_lp=AO_dat_app;
        for JJ=1:LP
            AO_dat_lp=AO_dat_lp+vinc;
            AO_dat_set=AO_dat_lp+voffset;
            putsample(AO,AO_dat_set);
            wait(AO,5);
            pause(5);
        end
%
        AO_dat_set=AO_dat+voffset
        putsample(AO,AO_dat_set);
        wait(AO,5);
        AO_dat_app=AO_dat;
        pause(5);
    end
%
elseif choice == 3
%    
    AO_dat=voffset;
    putsample(AO,AO_dat);
    wait(AO,5);
%
elseif choice == 4
%
    AI = analoginput('nidaq',Dev_ID);
    AICH = addchannel(AI,1);
%    AIchans2=AI.Channel
%    AI.Channel
%    delete(ch)
    AI.Channel.Units='Volts';
    AI.Channel.InputRange=[-10 10];
    set(AI,'TriggerType','Immediate');
    set(AI,'SampleRate',10.0);
    set(AI,'SamplesPerTrigger',10);
    set(AI,'TriggerRepeat',0);
    start(AI);
    wait(AI,5);
    dat_out=getdata(AI);
    ZERO_VAL_DARK=sum(dat_out./10);
    stop(AI);
    clear AI;
    AI = analoginput('nidaq',Dev_ID);
    AICH = addchannel(AI,0);
%    AIchans3=AI.Channel
    AI.Channel.Units='Volts';
    AI.Channel.InputRange=[-10 10];
    plot(dat_out,'bo');
    xlabel('Sample Number');
    ylabel('Dark Current, V (~1e-6 A/V)');
    title('REST CURRENT SHOULD BE LESS THAN 0.5 V');
%
elseif choice == 5
%
    scan_ans=inputdlg(scan_prompt,scan_title,scan_num_lines,scan_def);
%
    if ~isempty(scan_ans)   % if response is valid
%
        scans=str2num(char(scan_ans));
        if scans <=0
            scans=1;
        elseif scans > 10
            scans=10;
        end
    %
        Z=zeros(8,8,scans);
        Zold=zeros(8,8);
        DIV=ones(8,8);
        div_v=zeros(64,1);
 %
 %      BEGIN SCAN LOOP
 %
 LL1=1;
%        for LL1=1:scans
        while LL1 <= scans
 %
 %  Get dark value
 %
            set(AI,'TriggerType','Immediate');
            set(AI,'SampleRate',10.0);
            set(AI,'SamplesPerTrigger',10);
            set(AI,'TriggerRepeat',0);
            start(AI);
            wait(AI,20);
            dat_out=getdata(AI);
            ZERO_VAL=sum(dat_out./10);
            pause(3);
%
            set(AI,'TriggerType','HwDigital');
            set(AI,'HwDigitalTriggerSource','PFI0');
            set(AI,'TriggerCondition','NegativeEdge');
            set(AI,'SampleRate',5);
            set(AI,'SamplesPerTrigger',2);
            set(AI,'TriggerRepeat',ITR);
            pause(3);
%
%
%            diag1=daqmem;
%            memload=['Memory Load: ',num2str(diag1.MemoryLoad)];
%            totphys=['Total Phys: ',num2str(diag1.TotalPhys)];
%            availphys=['Avbailable Phys: ',num2str(diag1.AvailPhys)];
%            totpgfile=['Total Page File: ',num2str(diag1.TotalPageFile)];
%            availpgfile=['Available Page File: ',num2str(diag1.AvailPageFile)];
%            totvirt=['Total Virtual: ',num2str(diag1.TotalVirtual)];
%            availvirt=['Available Virtual: ',num2str(diag1.AvailVirtual)];
%            usedq=['Used by DAQ: ',num2str(diag1.UsedDaq)];
%            init_message={memload, totphys, availphys, totpgfile, availpgfile, totvirt, availvirt, usedq};
%            h = msgbox(init_message,'memory use');
%
%
            start(AI);
            pause(5);
            putvalue(DIO,dio_dat_low);      %Set DIO line 0 low to start pulsing
            t1=clock;                       % get time when pulsing begins
            pause(0.1);
            putvalue(DIO,dio_dat_hi);      %Set DIO line 0 hi to stop pulsing
            samps=0;
%
            TMPDAT=ones(64,2).*ZERO_VAL;
            dat_mat(:,:,1)=(reshape(TMPDAT(:,1),8,8));
            dat_mat(:,:,2)=(reshape(TMPDAT(:,2),8,8));
            subplot(1,1,1,'replace');
%
            Z(:,:,LL1)=(dat_mat(:,:,1)-ZERO_VAL);
            Zav=sum(Z,3)./DIV;
%
            h=bar3(mult.*Zav-min(min(mult.*Zav)));
            xlabel('Columns');
            ylabel('Rows');
            colormap jet;
            colorbar;
            shading interp;
            for i = 1:length(h)
                zdata = get(h(i),'Zdata');
                set(h(i),'Cdata',zdata);
                set(h,'EdgeColor','k');
            end
            caxis([0 5.0]);
%
            title(['Scan number = ',num2str(LL1),' of ',num2str(scans),'; applied potential = ',num2str(-AO_dat_app)]);
            hold on
            trigs=0;
            TO=-1;            % elapsed time less than timeout condition (70 seconds)
            div_v=zeros(64,1);
%
            while (trigs < ITR+1)&(TO < 0)    % reading during acquisition
                samps=get(AI,'SamplesAcquired');
                trigs=get(AI,'TriggersExecuted');
                if (samps > 7)
                    tmpdat=peekdata(AI,samps);
%                    tmpdat_size = size(tmpdat)
                    tmpdat_out=reshape([tmpdat(1:2.*floor(samps./2))],2,floor(samps./2))';
                    [rtd,ctd]=size(tmpdat_out);
                    tmpdat_out=[tmpdat_out(1,:); tmpdat_out(3:rtd,:)];
                    [rtd,ctd]=size(tmpdat_out);
                    if LL1 > 1
                        div_v(1:rtd)=1;
                        div=(reshape(div_v,8,8));
                        div=transL*div*transR;
                        DIV_tmp=DIV+div;
                    else
                        DIV_tmp=DIV;
                    end
                    TMPDAT(1:rtd,:)=tmpdat_out;
                    dat_mat(:,:,1)=(reshape(TMPDAT(:,1),8,8));
                    dat_mat(:,:,2)=(reshape(TMPDAT(:,2),8,8));
                    dat_mat(:,:,1)=transL*dat_mat(:,:,1)*transR;
                    dat_mat(:,:,2)=transL*dat_mat(:,:,2)*transR;
                    subplot(1,1,1,'replace');
%
                    Z(:,:,LL1)=(dat_mat(:,:,1)-ZERO_VAL);
                    Zav=sum(Z,3)./DIV_tmp;
%
                    h=bar3(mult.*Zav-min(min(mult.*Zav)));
                    xlabel('Columns');
                    ylabel('Rows');
                    title(['Scan number = ',num2str(LL1),' of ',num2str(scans),'; applied potential = ',num2str(-AO_dat_app)]);
%
                    colormap jet;
                    colorbar;
                    shading interp;
                    for i = 1:length(h)
                        zdata = get(h(i),'Zdata');
                        set(h(i),'Cdata',zdata);
                        set(h,'EdgeColor','k');
                    end
                    caxis([0 5.0]);
                    drawnow;
                end
                t2=clock;            % current time
                delt=etime(t2,t1);   % time since pulsing started
                if delt > 70        % pulser timeout condition
                    TO = 1;
                end
                pause(1)
            end
            hold off
            if TO < 0       % condition indicating a good data set
                wait(AI,5);
                samps=get(AI,'SamplesAcquired');
                pause(1);
                dat_out_stream=getdata(AI,samps);
%
                stop(AI);
%                dat_out_stream_size = size(dat_out_stream)
                dat_out_tmp=reshape([dat_out_stream;1],3,samps./2)';
%
                dat_out=[dat_out_tmp(1,1:2); dat_out_tmp(3:samps./2,1:2)];
                dat_mat(:,:,1)=(reshape(dat_out(:,1),8,8));
                dat_mat(:,:,2)=(reshape(dat_out(:,2),8,8));
                dat_mat(:,:,1)=transL*dat_mat(:,:,1)*transR;
                dat_mat(:,:,2)=transL*dat_mat(:,:,2)*transR;
                hold off
%
                subplot(1,1,1,'replace');
%
                Z(:,:,LL1)=(dat_mat(:,:,1)-ZERO_VAL);
%
                Zav=sum(Z,3)./LL1;
                h=bar3(mult.*Zav-min(min(mult.*Zav)));
                xlabel('Columns');
                ylabel('Rows');
                title(['Scan number = ',num2str(LL1),' of ',num2str(scans),'; applied potential = ',num2str(-AO_dat_app)]);
%
                colormap jet;
                colorbar;
                shading interp;
                for i = 1:length(h)
                    zdata = get(h(i),'Zdata');
                    set(h(i),'Cdata',zdata);
                    set(h,'EdgeColor','k');
                end
                caxis([0 5.0]);
                drawnow;
%
                DIV=ones(8,8).*LL1;
                %
                LL1=LL1+1;      % successful scan, increment scan counter
                %
            else                % missed a trigger in the scan
                stop(AI);
                pause(1);
                samps=get(AI,'SamplesAcquired');
                dat_out_stream=getdata(AI,samps);
%
                subplot(1,1,1,'replace');
%
                LL1_1=max(1,LL1-1);
                Zav=sum(Z,3)./LL1_1;
                h=bar3(mult.*Zav-min(min(mult.*Zav)));
                xlabel('Columns');
                ylabel('Rows');
                title(['Scan number = ',num2str(LL1-1),' of ',num2str(scans),'; applied potential = ',num2str(-AO_dat_app),' MISSED TRIGGER ON LAST SCAN!']);
%
                colormap jet;
                colorbar;
                shading interp;
                for i = 1:length(h)
                    zdata = get(h(i),'Zdata');
                    set(h(i),'Cdata',zdata);
                    set(h,'EdgeColor','k');
                end
                caxis([0 5.0]);
            end
%
%
        end
%
%   END OF SCAN LOOP
%
        Zav=sum(Z,3)./scans;
        std_dev=zeros(8,8);
        for jj=1:scans
          std_dev=std_dev+((Z(:,:,jj)-Zav).^2);
        end
        std_dev=sqrt(std_dev./scans);
        Z_out=mult.*Zav-min(min(mult.*Zav));
%
    end
%
elseif choice == 6
    %
    stat=shark_fig_conv_6(Z_out,std_dev,-AO_dat_app,ZERO_VAL_DARK,scans);
    %
elseif choice == 7
    %   I/V scan
    CrMd.WindowStyle='replace';
    CrMd.Interpreter='Tex';
%
    IV_txt={'{\bf{I/V Scanning:}}';
         ' 0 \rightarrow V1 \rightarrow V2 \rightarrow 0';       
        'Scans start at 0 V';
        'Scan proceeds to V1';
        'Scan changes direction and goes to V2';
        'If V2 = 0 V, scan stops';
        'Otherwise, scan changes direction at V2';
        '     and returns to 0 V'};
    IV_msg=msgbox(IV_txt,'I/V Scanning','help','replace');
    IVpos=get(IV_msg,'Position');
    IVpos(1)=IVpos(1)-IVpos(3);
    set(IV_msg,'Position',IVpos);
%
    IV_prompt={'V1 (-0.5 < Volts < 1.5)','V2 (-0.5 < Volts < 1.5)', 'Scan Rate (< 0.1 V/s)'};
    IV_dlg_title='I/V Scan Parameters';
    IV_num_lines=1;
    IV_def={'1','-0.5','0.1'};
    IV_ans=inputdlg(IV_prompt,IV_dlg_title,IV_num_lines,IV_def);
    
    close(IV_msg);      % close the message box
    
    if ~isempty(IV_ans)
%   Zero the output voltage        
        putsample(AO,voffset);
        wait(AO,5)
%
        V1=str2num(char(IV_ans(1)));
        V2=str2num(char(IV_ans(2)));
        Rate=str2num(char(IV_ans(3)));
%
        if V1 > 0  % positive first
            direc = 1;
            if V1 > 1.5
                V1 = 1.5;
            end
            if V2 >= 0
                legs=2;
                V2=0;
            else
                legs=3;
                if V2 < -0.5
                    V2=-0.5;
                end
            end
        else            % negative first
            direc = -1;
            if V1 < -0.5
                V1 = -0.5;
            end
            if V2 <= 0
                legs=2;
                V2=0;
            else
                legs=3;
                if V2 > 1.5
                    V2=1.5;
                end
            end
        end
%
%
    V_Scan1=[0:direc.*0.025:V1];
    if legs == 2
        V_Scan=[V_Scan1, fliplr(V_Scan1(1:end-1))];
    else
        V_Scan2=[V_Scan1(end-1):direc.*(-1).*0.025:V2];
        V_Scan3=[V_Scan2(end-1):direc.*0.025:0];
        V_Scan=[V_Scan1, V_Scan2, V_Scan3];
    end
    plot(V_Scan,'o')
    pause
    %
    steps = length(V_Scan)
    %
    if Rate > 0.1
        Rate = 0.1;
    end
    tau = 1./(40.*Rate)
    tau=tau./2;
    %
    %
    AI = analoginput('nidaq',Dev_ID);
    AICH = addchannel(AI,1);
    AI.Channel.Units='Volts';
    AI.Channel.InputRange=[-20 20];
    set(AI,'TriggerType','Immediate');
    set(AI,'SampleRate',1000.*Rate);
    set(AI,'SamplesPerTrigger',10);
    set(AI,'TriggerRepeat',0);
    %
    pause(1);
    tic;
    clear I_dat
    for IV_LP=2:steps
        %
        %IV_LP
        %V_Scan(IV_LP)
        %   wait half the time interval
        dt=toc;
        while dt < tau
            dt=toc;
        end
        tic;
%        read the current
        start(AI);
        wait(AI,5);
        dat_out=getdata(AI);
        stop(AI);
        %   wait another half the time interval
        dt=toc;
        while dt < tau
            dt=toc;
        end
        tic;
        %   set new voltage
        %   add offset voltage
        Vset=-V_Scan(IV_LP)+voffset;
        putsample(AO,Vset);
        wait(AO,5);
        %   process data
        I_dat(IV_LP-1)=sum(dat_out./10);
        %
    end
%        
        dt=toc;
        while dt < tau
            dt=toc;
        end
%        read the current
        start(AI);
        wait(AI,5);
        dat_out=getdata(AI);
        stop(AI);
        I_dat(steps)=sum(dat_out./10);
    clear AI;
    plot(V_Scan,I_dat)
    grid on
    xlabel('Cell Voltage');
    ylabel('Current, {\mu}A');
    title('I/V Scan');
    %   reset analog input
    AI = analoginput('nidaq',Dev_ID);
    AICH = addchannel(AI,0);
    AI.Channel.Units='Volts';
    AI.Channel.InputRange=[-10 10];
%
    end
%
elseif choice == 8
    %
    stat=web('http://www.bilrc.caltech.edu/solmatdisc','-browser');
    %
end
%   turn off applied voltage
%
%
end
%
close all
AO_dat=voffset;
putsample(AO,AO_dat);
wait(AO,1);
stop(AO);
stop(AI);
stat_out=1;
%
%if isempty(dat_out)
%    dat_out=0;
%elseif isempty(dat_mat)
%    dat_mat=0;
%end