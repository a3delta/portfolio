
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

entity OR_block is
    Port ( x : in STD_LOGIC;
           y : in STD_LOGIC;
           g : out STD_LOGIC);
end OR_block;

architecture DataFlow of OR_block is

begin

    g <= x OR y;

end DataFlow;
