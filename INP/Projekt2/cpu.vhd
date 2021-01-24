-- cpu.vhd: Simple 8-bit CPU (BrainF*ck interpreter)
-- Copyright (C) 2019 Brno University of Technology,
--                    Faculty of Information Technology
-- Author(s): Tomáš Hrúz (xhruzt00)
--

library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;

-- ----------------------------------------------------------------------------
--                        Entity declaration
-- ----------------------------------------------------------------------------
entity cpu is
 port (
   CLK   : in std_logic;  -- hodinovy signal
   RESET : in std_logic;  -- asynchronni reset procesoru
   EN    : in std_logic;  -- povoleni cinnosti procesoru
 
   -- synchronni pamet RAM
   DATA_ADDR  : out std_logic_vector(12 downto 0); -- adresa do pameti
   DATA_WDATA : out std_logic_vector(7 downto 0); -- mem[DATA_ADDR] <- DATA_WDATA pokud DATA_EN='1'
   DATA_RDATA : in std_logic_vector(7 downto 0);  -- DATA_RDATA <- ram[DATA_ADDR] pokud DATA_EN='1'
   DATA_RDWR  : out std_logic;                    -- cteni (0) / zapis (1)
   DATA_EN    : out std_logic;                    -- povoleni cinnosti
   
   -- vstupni port
   IN_DATA   : in std_logic_vector(7 downto 0);   -- IN_DATA <- stav klavesnice pokud IN_VLD='1' a IN_REQ='1'
   IN_VLD    : in std_logic;                      -- data platna
   IN_REQ    : out std_logic;                     -- pozadavek na vstup data
   
   -- vystupni port
   OUT_DATA : out  std_logic_vector(7 downto 0);  -- zapisovana data
   OUT_BUSY : in std_logic;                       -- LCD je zaneprazdnen (1), nelze zapisovat
   OUT_WE   : out std_logic                       -- LCD <- OUT_DATA pokud OUT_WE='1' a OUT_BUSY='0'
 );
end cpu;


-- ----------------------------------------------------------------------------
--                      Architecture declaration
-- ----------------------------------------------------------------------------
architecture behavioral of cpu is


  signal pc_inc : std_logic;
  signal pc_dec : std_logic;
  signal pc_reg : std_logic_vector(11 downto 0);

  signal ptr_inc : std_logic;
  signal ptr_dec : std_logic;
  signal ptr_reg : std_logic_vector(11 downto 0);
  signal ptr_reg_mux2 : std_logic_vector(11 downto 0);

  -- signal cnt_inc : std_logic;
  -- signal cnt_dec : std_logic;
  -- signal cnt_reg : std_logic_vector(7 downto 0);

  signal sel1 : std_logic;
  signal sel2 : std_logic;
  signal sel3 : std_logic_vector(1 downto 0);

  type FSMstate is (
    s_first, -- startovaci stav
    s_fetch, -- nacitanie instrukcie
    s_decode, -- dekodovanie instrukcie
    s_inc, -- inkrementace hodnoty ukazatele
    s_dec, -- dekrementace hodnoty ukazatele
    s_act_inc, -- inkrementace hodnoty aktualni bunky
    s_act_inc2,
    s_act_dec, -- dekrementace hodnoty aktualni bunky
    s_act_dec2,
    s_while_start, -- je-li hodnota aktualni bunky nulova, skoc za odpovidajici prikaz ] jinak pokracuj nasledujicim znakem
    s_while_start2,
    s_while_start3,
    s_while_start4,
    s_while_end, -- jeli hodnota aktualni bunky nenulova, skoc za odpovi dajici prikaz [ jinak pokracuj nasledujicim znakem
    s_while_end2,
    s_while_end3,
    s_while_end4,
    s_print, --  vytiskni hodnotu aktualni bunky
    s_print2,
    s_get, -- nacti hodnotu a uloz ji do aktualni bunky
    s_get2,
    s_ptr_to_temp, -- uloz hodnotu bunky do pomocne promenne
    s_ptr_to_temp2,
    s_temp_to_ptr, -- hodnotu pomocne promenne uloz do aktualni bunky
    s_temp_to_ptr2,
    s_return, -- zastav vykonavani programu
    s_others
    );
    signal pstate : FSMstate;
    signal nstate : FSMstate;

begin

 -- zde dopiste vlastni VHDL kod


 -- pri tvorbe kodu reflektujte rady ze cviceni INP, zejmena mejte na pameti, ze 
 --   - nelze z vice procesu ovladat stejny signal,
 --   - je vhodne mit jeden proces pro popis jedne hardwarove komponenty, protoze pak
 --   - u synchronnich komponent obsahuje sensitivity list pouze CLK a RESET a 
 --   - u kombinacnich komponent obsahuje sensitivity list vsechny ctene signaly.


 --automat na ovladanie signalov


	-- program counter (PC)
	pc_cntr: process (CLK, RESET)
	begin
		if RESET = '1' then
			pc_reg <= (others => '0');
    elsif CLK'event and CLK = '1' then
      if pc_inc = '1' then
        pc_reg <= pc_reg + 1;
      elsif pc_dec = '1' then
        pc_reg <= pc_reg - 1;
      end if ;
		end if;
  end process;

  --pointer counter (PTR)
  ptr_cntr: process (CLK, RESET)
	begin
		if RESET = '1' then
			ptr_reg <= (others => '0');
    elsif CLK'event and CLK = '1' then
      if ptr_inc = '1' then
        ptr_reg <= ptr_reg + 1;
      elsif ptr_dec = '1' then
        ptr_reg <= ptr_reg - 1;
      end if;
    end if;
  end process;

  --CNT
  -- cnt_cntr: process (CLK, RESET)
	-- begin
	-- 	if RESET = '1' then
	-- 		cnt_reg <= (others => '0');
  --   elsif CLK'event and CLK = '1' then
  --     if cnt_inc = '1' then
  --       cnt_reg <= cnt_reg + 1;
  --     elsif ptr_dec = '1' then
  --       cnt_reg <= cnt_reg - 1;
  --     end if;
	-- 	end if;
  -- end process;


  --Multiplexor1
  multiplexor1: process (sel1, pc_reg, ptr_reg_mux2)
  begin
    case sel1 is   
      when '0' => DATA_ADDR <= '0' & pc_reg;
      when others => DATA_ADDR <= '1' & ptr_reg_mux2;
    end case;
  end process;


  --Multiplexor2
  multiplexor2: process (sel2, ptr_reg)
  begin
    case sel2 is   
      when '0' => ptr_reg_mux2 <= "000000000000";
      when others => ptr_reg_mux2 <= ptr_reg;
    end case;
  end process;

  --Multiplexor3
  multiplexor3: process (sel3, IN_DATA, DATA_RDATA)
  begin
    case sel3 is   
      when "00" => DATA_WDATA <= IN_DATA;
      when "01" => DATA_WDATA <= DATA_RDATA - 1;
      when "10" => DATA_WDATA <= DATA_RDATA + 1;
      when others => DATA_WDATA <= DATA_RDATA;
    end case;
  end process;

  --Present State registr
  pstatereg: process(RESET, CLK)
  begin
    if (RESET='1') then
      pstate <= s_first;
    elsif (EN='1') then
      if (CLK'event) and (CLK='1') then
        pstate <= nstate;
      end if; 
    end if;
  end process;



--Next State logic, Output logic (FSM)
nstate_logic: process(pstate, DATA_RDATA, OUT_BUSY, IN_VLD)
begin
  -- default values
  nstate <= s_first;
  DATA_EN <= '0';
  DATA_RDWR <= '0';
  sel1 <= '0';
  sel2 <= '0';
  sel3 <= "00";
  pc_inc <= '0';
  pc_dec <= '0';
  ptr_inc <= '0';
  ptr_dec <= '0';
 -- cnt_inc <= '0';
  --cnt_dec <= '0';
  OUT_DATA <= "00000000";
  OUT_WE <= '0';
  IN_REQ <= '0';




  --logika
  case pstate is

    --pociatocny stav
    when s_first =>
      nstate <= s_fetch;

    --nacitanie instrukcie
    when s_fetch =>
      nstate <= s_decode;
      DATA_EN <= '1';
      DATA_RDWR <= '0'; --citanie
      sel1 <= '0';
  
    -- dekodovanie instrukcie
    when s_decode =>
    --dekoder prikazov
      case DATA_RDATA is
        when X"3E" => nstate <= s_inc;
        when X"3C" => nstate <= s_dec;
        when X"2B" => nstate <= s_act_inc;
        when X"2D" => nstate <= s_act_dec;
        when X"5B" => nstate <= s_while_start;
        when X"5D" => nstate <= s_while_end;
        when X"2E" => nstate <= s_print;
        when X"2C" => nstate <= s_get;
        when X"24" => nstate <= s_ptr_to_temp;
        when X"21" => nstate <= s_temp_to_ptr;
        when X"00" => nstate <= s_return;
        when others => nstate <= s_others;
      end case; 

          --v kazdej instrukcii nastavim pc_inc na 1 a potom to poslem do fetch

      --inkrementacia >
    when s_inc =>
        pc_inc <= '1';
        ptr_inc <= '1';
        nstate <= s_fetch;


      --dekrementacia <
    when s_dec =>
        pc_inc <= '1';
        ptr_dec <= '1';
        nstate <= s_fetch;


      --inkrementacia aktualnej bunky +
    when s_act_inc =>
        pc_inc <= '1';
        DATA_EN <= '1';
        DATA_RDWR <= '0'; --citanie
        sel2 <= '1';
        sel1 <= '1'; 
        nstate <= s_act_inc2;
    when s_act_inc2 =>
        sel3 <= "10";
        DATA_EN <= '1';
        DATA_RDWR <= '1'; --zapis
        sel2 <= '1';
        sel1 <= '1'; 
        nstate <= s_fetch;


      --dekrementacia aktualnej bunky -
    when s_act_dec =>
      pc_inc <= '1';
      DATA_EN <= '1';
      DATA_RDWR <= '0'; --citanie
      sel2 <= '1';
      sel1 <= '1'; 
      nstate <= s_act_dec2;
    when s_act_dec2 =>
      sel3 <= "01";
      DATA_EN <= '1';
      DATA_RDWR <= '1'; --zapis
      sel2 <= '1';
      sel1 <= '1'; 
      nstate <= s_fetch;

      
      --print .
    when s_print =>
      pc_inc <= '1';
      DATA_EN <= '1';
      DATA_RDWR <= '0'; --citanie
      sel2 <= '1';
      sel1 <= '1'; 
      nstate <= s_print2;
    when s_print2 =>
      if (OUT_BUSY = '0') then
        OUT_DATA <= DATA_RDATA;
        OUT_WE <= '1';
        nstate <= s_fetch;
      else
        nstate <= s_print2;
      end if ;

    
    --get ,
    when s_get =>
      pc_inc <= '1';
      IN_REQ <= '1';
      nstate <= s_get2;
    when s_get2 =>
      if (IN_VLD = '1') then
        DATA_EN <= '1';
        DATA_RDWR <= '1'; --zapis
        sel3 <= "00";
        sel2 <= '1';
        sel1 <= '1';
        nstate <= s_fetch;
      else
        IN_REQ <= '1';
        nstate <= s_get2;
      end if ;

    
    --*ptr to temp $
    when s_ptr_to_temp =>
      pc_inc <= '1';
      DATA_EN <= '1';
      DATA_RDWR <= '0'; --citanie
      sel2 <= '1';
      sel1 <= '1'; 
      nstate <= s_ptr_to_temp2;
    when s_ptr_to_temp2 =>
      sel3 <= "11";
      DATA_EN <= '1';
      DATA_RDWR <= '1'; --zapis
      sel2 <= '0';
      sel1 <= '1'; 
      nstate <= s_fetch;


    --temp to *ptr !
    when s_temp_to_ptr =>
      pc_inc <= '1';
      DATA_EN <= '1';
      DATA_RDWR <= '0'; --citanie
      sel2 <= '0';
      sel1 <= '1'; 
      nstate <= s_temp_to_ptr2;
    when s_temp_to_ptr2 =>
      sel3 <= "11";
      DATA_EN <= '1';
      DATA_RDWR <= '1'; --zapis
      sel2 <= '1';
      sel1 <= '1'; 
      nstate <= s_fetch;
      

    --while start [
    when s_while_start =>
      pc_inc <= '1';
      DATA_EN <= '1';
      DATA_RDWR <= '0'; --citanie
      sel2 <= '1';
      sel1 <= '1'; 
      nstate <= s_while_start2;
    --zistujem ci su data 0, ak su 0 nacitavam dalsiu instrukciu na preskocenie vo while
    when s_while_start2 =>
      if (DATA_RDATA = "00000000") then
        nstate <= s_while_start3;
        DATA_EN <= '1';
        DATA_RDWR <= '0';
        sel1 <= '0'; 
      else
        nstate <= s_fetch;

      end if;
    -- dekodujem ci neni ]
    when s_while_start3 =>
      if DATA_RDATA /= X"5D" then
        pc_inc <= '1'; 
        nstate <= s_while_start4;
      else
        pc_inc <= '1';
        nstate <= s_fetch;
      end if;
    --nacitavanie instrukcie pred dekodovanim v stave 3
    when s_while_start4 =>
      nstate <= s_while_start3;
      DATA_EN <= '1';
      DATA_RDWR <= '0';
      sel1 <= '0'; 
        
    
    --while end ]
    when s_while_end =>
      pc_inc <= '1';
      DATA_EN <= '1';
      DATA_RDWR <= '0'; --citanie
      sel2 <= '1';
      sel1 <= '1';
      nstate <= s_while_end2;
    --zistujem ci su data 0, ak su 0 nacitavam instrukciu za while
    when s_while_end2 =>
      if (DATA_RDATA = "00000000") then
        nstate <= s_fetch;
      else
        nstate <= s_while_end3;
        pc_dec <= '1';
      end if;
    --dekodujem ci je [
    when s_while_end3 =>
    if DATA_RDATA /= X"5B" then
      pc_dec <= '1';
      nstate <= s_while_end4;
    else
      pc_inc <= '1';
      nstate <= s_fetch;
    end if;
    --nacitavanie instrukcie pred dekodovanim v stave 3
    when s_while_end4 =>
      nstate <= s_while_end3;
      DATA_EN <= '1';
      DATA_RDWR <= '0';
      sel1 <= '0'; 

    --return null
    when s_return =>
      nstate <= s_return;
    
    --ine stavy
    when s_others =>
      pc_inc <= '1';
      nstate <= s_fetch;
   
    when others =>
      null;
   
  end case ;

end process;

end behavioral;
 
