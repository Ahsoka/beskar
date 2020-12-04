function [stat]=shark_fig_conv_5(Dat_out,std_dev,App_volt,Dark_current,Scans)
%
%
ichem=0;
ipat=0;
options.Resize='on';
options.WindowStyle='normal';
options.Interpreter='tex';
%
Exp_Inf={' ',' ',' ',' ',' ',' ',' '};
layer_pattern=zeros(8,8,6);
Element_cell={'Aluminum','Barium','Cerium','Cobalt','Copper','Iron','Lanthanum','Manganese','Nickel','Yttrium','Zinc'};
Element_tab={'H',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','He';
          'Li','Be',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','B','C','N','O','F','Ne';
          'Na','Mg',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','Al','Si','P','S','Cl','Ar';
          'K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn','Ga','Ge','As','Se','Br','Kr';
          'Rb','Sr','Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In','Sn','Sb','Te','I','Xe';
          'Cs','Ba','La','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg','Tl','Pb','Bi','Po','At','Rn';
          'Fr','Ra','Ac',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ';
          'Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu',' ',' ',' ',' ';
          'Th','Pa','U','Np','Pu','Am','Cm','Bk','Cf','Es','Fm','Md','No','Lr',' ',' ',' ',' '};
Element_name={'Hydrogen',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','Helium';
          'Lithium','Beryllium',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','Boron','Carbon','Nitrogen','Oxygen','Fluorine','Neon';
          'Sodium','Magnesium',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','Aluminum','Silicon','Phosphorous','Sulfur','Chlorine','Argon';
          'Potassium','Calcium','Scandium','Titanium','Vanadium','Chromium','Manganese','Iron','Cobalt','Nickel','Copper','Zinc','Gallium','Germanium','Arsenic','Seleniium','Bromine','Krypton';
          'Rubidium','Strontium','Yttrium','Zirconium','Niobium','Molybdenum','Technetium','Ruthenium','Rhodium','Palladium','Silver','Cadmium','Indium','Tin','Antimony','Tellurium','Iodine','Xenon';
          'Cesium','Barium','Lanthanum','Halfnium','Tantalum','Tungsten','Rhenium','Osmiium','Iridium','Platinum','Gold','Mercury','Thallium','Lead','Bismuth','Polonium','Astatine','Radon';
          'Francium','Radium','Actinium',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ';
          'Cerium','Praeseodymium','Neodymium','Promethium','Samarium','Europium','Gadolinium','Terbium','Dysprosium','Holmium','Erbium','Thulium','Ytterbium','Lutetium',' ',' ',' ',' ';
          'Thorium','Protactinium','Uranium','Neptunium','Plutonium','Americium','Curium','Berkelium','Californium','Einsteinium','Fermium','Mendelevium','Nobelium','Lawrencium',' ',' ',' ',' '};
      %
%
Patterns(1:8,1:8,1)={'[0:7:0]','[0:6:1]','[0:5:2]','[0:4:3]','[0:3:4]','[0:2:5]','[0:1:6]','[0:0:7]';
                     '[1:6:0]','[1:5:1]','[1:4:2]','[1:3:3]','[1:2:4]','[1:1:5]','[1:0:6]','[0:0:0]';
                     '[2:5:0]','[2:4:1]','[2:3:2]','[2:2:3]','[2:1:4]','[2:0:5]','[0:0:0]','[0:0:0]';
                     '[3:4:0]','[3:3:1]','[3:2:2]','[3:1:3]','[3:0:4]','[0:0:0]','[0:0:0]','[0:0:0]';
                     '[4:3:0]','[4:2:1]','[4:1:2]','[4:0:3]','[0:0:0]','[0:0:0]','[0:0:0]','[0:0:0]';
                     '[5:2:0]','[5:1:1]','[5:0:2]','[0:0:0]','[0:0:0]','[0:0:0]','[0:0:0]','[0:0:0]';
                     '[6:1:0]','[6:0:1]','[0:0:0]','[0:0:0]','[0:0:0]','[0:0:0]','[0:0:0]','[0:0:0]';
                     '[7:0:0]','[0:0:0]','[0:0:0]','[0:0:0]','[0:0:0]','[0:0:0]','[0:0:0]','[0:0:0]'};

Patterns(1:8,1:8,2)={'[0:9:0]','[0:8:1]','[0:7:2]','[0:6:3]','[0:5:4]','[0:4:5]','[0:3:6]','[0:2:7]';
                     '[1:8:0]','[1:7:1]','[1:6:2]','[1:5:3]','[1:4:4]','[1:3:5]','[1:2:6]','[1:1:7]';
                     '[2:7:0]','[2:6:1]','[2:5:2]','[2:4:3]','[2:3:4]','[2:2:5]','[2:1:6]','[2:0:7]';
                     '[3:6:0]','[3:5:1]','[3:4:2]','[3:3:3]','[3:2:4]','[3:1:5]','[3:0:6]','[0:0:0]';
                     '[4:5:0]','[4:4:1]','[4:3:2]','[4:2:3]','[4:1:4]','[4:0:5]','[0:0:0]','[0:1:8]';
                     '[5:4:0]','[5:3:1]','[5:2:2]','[5:1:3]','[5:0:4]','[0:0:0]','[1:0:8]','[0:0:9]';
                     '[6:3:0]','[6:2:1]','[6:1:2]','[6:0:3]','[0:0:0]','[8:0:1]','[0:0:0]','[0:0:0]';
                     '[7:2:0]','[7:1:1]','[7:0:2]','[0:0:0]','[8:1:0]','[9:0:0]','[0:0:0]','[0:0:0]'};
               
Patterns(1:8,1:8,3)={'[0]','[0]','[0]','[0]','[0]','[0]','[0]','[0]';
                     '[0]','[1]','[0]','[1]','[0]','[1]','[0]','[0]';
                     '[0]','[0]','[1]','[0]','[1]','[0]','[1]','[0]';
                     '[0]','[1]','[0]','[1]','[0]','[1]','[0]','[0]';
                     '[0]','[0]','[1]','[0]','[1]','[0]','[1]','[0]';
                     '[0]','[1]','[0]','[1]','[0]','[1]','[0]','[0]';
                     '[0]','[0]','[1]','[0]','[1]','[0]','[1]','[0]';
                     '[0]','[0]','[0]','[0]','[0]','[0]','[0]','[0]'};
%
PathName='';
choice = 0;
%
stat=0;
imeth=1;
ipass=1;
men_opts(1,:)={'Experiment Information','Load Chemical & Pattern Information from Excel File','Manually Load Chemical & Pattern Information','  ','  '};
men_opts(2,:)={'Experiment Information','Manually Load Chemical Information','Manually Load Pattern Information','Save the Data to a File',' '};
men_opts(3,:)={'Experiment Information','Load Chemical & Pattern Information from Excel File','Save the Data to a File','  ','  '};
men_ret={'Return'};
while choice < 6
    PathName='';
    main_opts=[men_opts(imeth,1:ipass),men_ret];
    ichoice = menu('Select an Option',main_opts);
    if imeth == 1
        if (ichoice == ipass+1)
            choice=10;
        elseif (ichoice == 1)
            choice=ichoice;
            ipass=3;
        elseif ichoice == 2
            imeth=3;
            choice=ichoice;
            ipass=2;
        elseif ichoice == 3
            imeth=2;
            choice = -1;
            ipass=2;
        end
    elseif imeth == 2
        if (ichoice == ipass+1)
            choice=10;
        elseif ichoice >= 2
            choice=ichoice+1;
        else
            choice=ichoice;
        end
        if ichoice==ipass
            ipass=min(ipass+1,4);
        end
    elseif imeth == 3
        if (ichoice == ipass+1)
            choice=10;
        elseif ichoice <= 2
            choice = ichoice;
        else
            choice = ichoice+2;
        end
        if ichoice==ipass
            ipass=min(ipass+1,3);
        end
    end
%    
%
if choice < 0
%
    stat=0;
%
elseif choice == 10;
    stat=1;
    return
    %
elseif choice == 1
    close all
    prompt = {'Your name (<20 char):',
              'Sample name (<20 char):',
              'LED Color',
              'General Comments (<256 char)'};
    dlg_title = 'Experiment Information';
    num_lines = 1;
    defaultanswer=Exp_Inf;
    Exp_Ans = inputdlg(prompt,dlg_title,num_lines,defaultanswer);
    if ~isempty(Exp_Ans)
        Exp_Inf=Exp_Ans;
    end
    %
    %
elseif choice == 2
    [ success, Custom_Pattern, Elements_xls, Els_xls, Chem_Inf_xls ] = get_xls_pattern( Element_name );
    if success==1
        Patterns(:,:,4)=Custom_Pattern;
        Pattern_num=4;
        Elements=Elements_xls;
        Els=Els_xls;
        Chem_Inf=Chem_Inf_xls;
        ichem=1;
        ipat=1;
        ipass=3;
    else
        ipass=2;
    end
%
elseif choice == 3
    clear Els;
    prompt = {'Enter the number of elements (1-6)'};
    dlg_title = 'Element Information';
    num_lines = 1;
    DefAns = {'3'};
    elements_char = inputdlg(prompt,dlg_title,num_lines,DefAns);
    if isempty(elements_char)
        elements_char={'0'};
    end
    Elements = str2num(char(elements_char));
%    Elements=3;
    for L3=1:Elements
        close all;
        axis;
        axis([0 19 0 10]);
        axis ij;
        axis off;
        title(['\bf{Select element #',num2str(L3),'}']);
        for L1=1:9
            for L2=1:18
                pl_dat=char(Element_tab(L1,L2));
                hhh(L1,L2)=text(L2-0.5,L1,pl_dat);
            end
        end
%
        cont=-1;
        while cont < 0
            [xpos,ypos]=ginput(1);
            xpos=round(xpos);
            ypos=round(ypos);
            if (xpos > 0) & (xpos < 19) & (ypos > 0) & (ypos < 10);
                Els(L3,1:2)=[xpos,ypos];
                cont=1;
                if L3 > 1
%                    l3m=L3-1
                for L4=1:1:L3-1
%                    l4=L4
%                    val=Els(L4,1:2)
                    if Els(L3,1:2)== Els(L4,1:2)
                        cont = -1;
                    end
                end
                end
                if cont > 0
                    close all
                end
            end
        end
%
        prompt = {[char(Element_name(Els(L3,2),Els(L3,1))),' salt used (<20 char):'],
                  [char(Element_name(Els(L3,2),Els(L3,1))),' concentration (M):']};
        dlg_title = 'Chem Info';
        num_lines=1;
        defaultanswer={'','0.04'};
        Chem_Inf_Ans = inputdlg(prompt,dlg_title,num_lines,defaultanswer,options);
        if ~isempty(Chem_Inf_Ans)
            Chem_Inf(:,L3)=Chem_Inf_Ans;
        else
            Chem_Inf(:,L3)={' ',' '};
        end
%
    ichem=1;
%
    end
%
elseif choice == 4
    close all;
    if Elements == 1
        H1=figure;
        set(H1,'Position',[500 200 750 500]);
        axis;
        axis([0 9 -1 9]);
        axis ij;
        axis off;
        title_text=['\bf{Spotting Position of ['];
        xlabel('Column Number');
        xlabel('Row Number');
    elseif Elements == 3
        H1=figure;
        set(H1,'Position',[150 200 1500 500]);
        axis;
        axis([0 18 -1 9]);
        axis ij;
        axis off;
        title_text=['\bf{Mixing Ratios of ['];
    else
        title_text=['\bf{Mixing Ratios of ['];        
    end
    for LL1=1:Elements
        title_text=[title_text,char(Element_name(Els(LL1,2),Els(LL1,1))),':'];
    end
    title_text=[title_text(1:length(title_text)-1),']}'];
    title(title_text);
%    
%    
    if Elements == 1                  % single chemical pattern
        hh=text(4.5,0,'\bf{Pattern 1}');
        set(hh,'HorizontalAlignment','center');
        for L1=1:8
            for L2=1:8
                pl_dat1=char(Patterns(L1,L2,3));
                hh=text(L2-0.3,L1,pl_dat1);
            end
        end
        hh=text(4.5,9,'\bf{Column Number}');
        set(hh,'HorizontalAlignment','center');
        hh=text(0.25,4.5,'\bf{Row Number}');
        set(hh,'HorizontalAlignment','right');
        Pattern_num = menu('Select the mixing pattern used','Pattern 1','Custom Pattern');
        if Pattern_num == 1
            Pattern_num=3;
        else
            [Custom_Pattern]=get_pattern_2(Elements,Element_name,Els);
            Patterns(:,:,4)=Custom_Pattern;
            Pattern_num=4;
        end
    elseif Elements == 3                       % 3-element chemical pattern
        hh=text(4,0,'\bf{Pattern 1}');
        hh=text(13,0,'\bf{Pattern 2}');
        set(hh,'HorizontalAlignment','center');
        xlabel('Column Number');
        xlabel('Row Number');
        for L1=1:8
            for L2=1:8
                pl_dat1=char(Patterns(L1,L2,1));
                hh=text(L2-0.3,L1,pl_dat1);
                pl_dat2=char(Patterns(L1,L2,2));
                hh=text(L2+9-0.3,L1,pl_dat2);
            end
        end
        hh=text(4.5,9,'\bf{Column Number}');
        set(hh,'HorizontalAlignment','center');
        hh=text(13.5,9,'\bf{Column Number}');
        set(hh,'HorizontalAlignment','center');
        hh=text(0.25,4.5,'\bf{Row Number}');
        set(hh,'HorizontalAlignment','right');
        Pattern_num = menu('Select the mixing pattern used','Pattern 1','Pattern 2','Custom Pattern');
        if Pattern_num == 3
            [Custom_Pattern]=get_pattern_2(Elements,Element_name,Els);
            Patterns(:,:,4)=Custom_Pattern;
            Pattern_num=4;
        end
    else
        [Custom_Pattern]=get_pattern_2(Elements,Element_name,Els);
        Patterns(:,:,4)=Custom_Pattern;
        Pattern_num=4;
    end
%
%    get(H1)
%
%    Pattern_num = menu('Select the mixing pattern used','Pattern 1','Pattern 2','Custom Pattern');
    close all
    ipat=1;
%
elseif (choice == 5)&(ipat==1)&(ichem==1)
    close all
    H1=figure;
    H1_Pos=get(H1,'Position');
    H1_Pos(1)=[H1_Pos(1)-200];
    set(H1,'Position',H1_Pos);
    hh=bar3(Dat_out);
%
    xlabel('Columns');
    ylabel('Rows');
    title_text=['\bf{Data from: ['];
    for LL1=1:Elements
        title_text=[title_text,char(Element_name(Els(LL1,2),Els(LL1,1))),':'];
    end
    title_text=[title_text(1:length(title_text)-1),']}'];
    title(title_text);
%    title(['\bf{Data from ',char(Element_name(Els(1,2),Els(1,1))),', ',char(Element_name(Els(2,2),Els(2,1))),', &',char(Element_name(Els(3,2),Els(3,1))),'}']);
    colormap jet
    colorbar
    shading interp
    for i = 1:length(hh)
        zdata = get(hh(i),'Zdata');
        set(hh(i),'Cdata',zdata);
        set(hh,'EdgeColor','k');
    end
    caxis([0 5.0]);
%
    H2=figure;
    H2_Pos=get(H2,'Position');
    H2_Pos(2)=[H2_Pos(2)-200];
    set(H2,'Position',H2_Pos);
    axis;
    axis([0 9 0 9]);
    axis ij;
    title('Mixing Pattern');
    for L1=1:8
        for L2=1:8
            pl_dat1=char(Patterns(L1,L2,Pattern_num));
            hh=text(L2-0.3,L1,pl_dat1);
        end
    end
    %
    H3=figure;
    H3_Pos=get(H3,'Position');
    H3_Pos(1:2)=[H3_Pos(1)+200, H3_Pos(2)-400];
    set(H3,'Position',H3_Pos);
    axis;
    axis([0 10 0 10]);
    axis off;
    prompt = {['Your name: ',char(Exp_Inf(1))],
              ['Sample name: ',char(Exp_Inf(2))],
              ['Applied Voltage: ',num2str(App_volt)],
              ['Dark Current Value: ',num2str(Dark_current)],
              ['Sumber of Scans: ',num2str(Scans)],
              ['LED Color: ',char(Exp_Inf(3))],
              ['General Comments: ',char(Exp_Inf(4))],
              ['    ']};
%          whos
    for L1=1:Elements
        prompt(8+((3.*L1)-2))={['Element #',num2str(L1),': ',char(Element_name(Els(L1,2),Els(L1,1)))]};
        prompt(8+((3.*L1)-1))={['Element #',num2str(L1),' Chemical: ',char(Chem_Inf(1,L1))]};
        prompt(8+(3.*L1))={['Element #',num2str(L1),' Concentration: ',char(Chem_Inf(2,L1)),' M']};
    end
%    prompt
    %
    text(1,5,prompt)
    svdat=menu(' Save these Data?','YES','NO');
    if svdat == 1
        strout=['\N;;'];
        strout=[strout,char(Exp_Inf(1)),';;\N;;',char(Exp_Inf(2)),';;',num2str(App_volt),';;',num2str(Dark_current),';;',num2str(Scans),';;',char(Exp_Inf(3)),';;',char(Exp_Inf(4)),';;'];
        for L1=1:Elements
            strout=[strout,char(Element_name(Els(L1,2),Els(L1,1))),';;',char(Chem_Inf(1,L1)),';;',char(Chem_Inf(2,L1)),';;'];
        end
        for L1=Elements+1:6
            strout=[strout,' ;;',' ;;',' ;;'];
        end
        patt_ind=zeros(Elements,2);
        for L1=1:8
            for L2=1:8
                strout=[strout,num2str(Dat_out(L1,L2)),';;',num2str(std_dev(L1,L2)),';;'];
                tmp=char(Patterns(L1,L2,Pattern_num));
                len_tmp=length(tmp);
                tmp_ind=find(tmp==':');
                if (isempty(tmp_ind))&(Elements == 1)
                    patt_ind(1,1:2)=[2,len_tmp-1];
                elseif length(tmp_ind)==(Elements-1)
                    patt_ind(1,1:2)=[2,tmp_ind(1)-1];
                    for LL1=2:Elements-1
                        patt_ind(LL1,1:2)=[tmp_ind(LL1-1)+1,tmp_ind(LL1)-1];
                    end
                    patt_ind(Elements,1:2)=[tmp_ind(Elements-1)+1,len_tmp-1];
                else
                    fprintf(' Inconsistent Pattern array ')
                    return
                end
                for L3=1:Elements
%                    tmp=char(Patterns(L1,L2,Pattern_num));
                    strout=[strout,tmp(patt_ind(L3,1):patt_ind(L3,2)),';;'];
                end
                for L3=Elements+1:6
                    strout=[strout,'0 ;;'];
                end
            end
        end
        %
        drawnow
%        close all
%        uiwait
        [FileName,PathName,FilterIndex] = uiputfile_fix([PathName,'*.smd'],['Save to a File']);
        pause(1);
        if FileName ~= 0
            fid=fopen([PathName,FileName],'w');                     % save the .smd file
            fprintf(fid,'%s',strout);
            fclose(fid);
            lenFN=length(FileName);
            saveas(H1,[PathName,FileName(1:lenFN-4)],'fig');        % save the .fig file
            close(H3);
            close(H2);
            view(0,90);
            caxis([0 5.0]);
            saveas(H1,[PathName,FileName(1:lenFN-4)],'bmp');        % save the .bmp file
            xlswrite([PathName,FileName(1:lenFN-4),'.xls'],Dat_out) % save the Excel file
        end
    end
    close all
    %
%
%
%
end
%
%
end
