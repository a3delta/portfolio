library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity LB4 is
    Port ( clk      : in    STD_LOGIC               := '0';
           n        : in    UNSIGNED(1 downto 0);
           reset    : in    STD_LOGIC               := '1';
           f        : out   UNSIGNED(3 downto 0));
end LB4;

architecture Behavioral of LB4 is

    SIGNAL state    : UNSIGNED(4 downto 0)  := "00000";
    SIGNAL x        : UNSIGNED(4 downto 0);
    SIGNAL prev     : UNSIGNED(2 downto 0)  := "100";

begin

    -- start up-counter process
    UPC: PROCESS(clk, reset)    -- triggers when clk or reset change
        BEGIN
            -- only run if at rising edge of clk and reset not triggered
            if (clk'event AND clk='1') then
            
                -- reset handling
                if (reset='0') then
                    state <= "00000";
                    f <= "0000";
                end if;
            
                -- test against prev n and reset state if needed
                if (prev="100") then        -- first run correction
                    prev <= '0' & n;
                elsif (prev(1 downto 0)=n) then
                    state <= "00000";
                end if;
                
                -- case statement for state management
                case state is
                    when "00000" =>     -- A state case
                        f <= "0000";
                    when "00001" =>     -- B state case
                        f <= "0001";
                    when "00010" =>     -- C state case
                        f <= n + "0001";
                    when others =>      -- other cases (x * n^x) + x
                        -- determine x
                        x <= state - "00001";
                        
                        -- if else for shortcut calcs
                        if (n="00") then    -- n = 0
                            f <= x(3 downto 0);
                        elsif (n="01") then -- n = 1
                            f <= x(3 downto 0) + x(3 downto 0);
                        elsif (n="10") then -- n = 2
                            f <= n & n; -- results in correct result
                            -- not scalable to a larger up-counter
                        end if;                       
                        
                end case;
                
                -- determine next state
                if (state="00010" AND n="11") then    -- 3 limit
                    state <= "00000";
                elsif (state="00011" AND n="10") then -- 2 limit
                    state <= "00000";
                elsif (state="01000" AND n="01") then -- 1 limit
                    state <= "00000";
                else                                  -- no limit
                    state <= state + "00001";
                end if;
            
            end if; -- end if for clk and reset check
    END PROCESS;
    -- end up-counter process

end Behavioral;
