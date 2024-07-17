library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity LB5 is
    Port ( w        : in  STD_LOGIC;
           seq      : in  STD_LOGIC_VECTOR(3 downto 0);
           clk      : in  STD_LOGIC;
           reset    : in  STD_LOGIC;
           z        : out STD_LOGIC := '0');
end LB5;

architecture Behavioral of LB5 is

    SIGNAL state : STD_LOGIC_VECTOR(2 downto 0) := "000";

begin

-- start sequence detector process
 SeqDetect: PROCESS(clk) -- triggers when clk changes
    BEGIN

    if (reset='0') then                 -- reset condition
        state <= "000";
        z <= '0';
    elsif (clk'event AND clk='1') then  -- no reset, process at rising edge

        -- case statement for state management
        case state is
            when "000" => -- state A case
                z <= '0';
                if (w=seq(3)) then      -- go to next state
                    state <= "001";
                end if;                 -- else stay
            when "001" => -- state B case
                z <= '0';
                if (w=seq(2)) then      -- go to next state
                    state <= "010";
                elsif (w/=seq(3)) then  -- go to start state
                    state <= "000";
                end if;                 -- else stay
            when "010" => -- state C case
                if (w=seq(1)) then      -- go to next state
                    state <= "011";
                elsif (w=seq(3)) then   -- go to prev state
                    state <= "001";
                else                    -- go to start state
                    state <= "000";
                end if;
            when "011" => -- state D case
                -- check seq detection
                if (w=seq(0)) then      -- go to next state
                    z <= '1';           -- seq detected
                end if;
                
                -- go to next state
                if (w=seq(3)) then   -- go to state B (1 bit overlap)
                    state <= "001";
                else                    -- go to state A
                    state <= "000";
                end if;
            when others => -- others
                -- nothing
        end case;

    end if; -- end if for clk and reset check

    END PROCESS;
    -- end sequence detector process

end Behavioral;
