// hadcoins ICO
pragma solidity ^0.5.6;

contract hadcoins_ico {

    // Max num of hadcoins to be in circulation 1 Mil
    uint public max_hadcoins = 1000000;
    
    // conversion rates from $ - HC  1$ = 1000 HC
    uint public usd_to_hadcoins = 1000;

    // Number of HCs bought by inverstors
    uint public total_hadcoins_bought = 0;

    // Mapping from the investor address to its equity in HC and $
    mapping(address => uint) equity_hadcoins;
    mapping(address => uint) equity_usd;

    // Check if the investor can buy and hadcoin
    modifier can_buy_hc (uint usd_invested) {
        require(usd_invested * usd_to_hadcoins + total_hadcoins_bought <= max_hadcoins);
        _;
    }

    // Getting the equity in hadcoins of an investor

    function equity_hc (address investor) external view returns(uint) {
        return equity_hadcoins[investor];
    }

    // Getting the equity in usd of an investor
    // function equity_usd (address investor) external view returns(uint) {
    //     return equity_usd[investor];
    // }

    function equity_usd (address investor) external view returns(uint) {
        return equity_usd[investor];
    }

    // Buying hadcoins
    function buy_hc(address investor, uint usd_invested) external can_buy_hc(usd_invested) {
        uint hadcoins_bought = usd_invested * usd_to_hadcoins;
        equity_hadcoins[investor] += hadcoins_bought;
        equity_usd[investor] += equity_hadcoins[investor] / usd_to_hadcoins;
        total_hadcoins_bought += hadcoins_bought;
    }

    // Selling HCs
    function sell_hc(address investor, uint had_coins) external {
        // uint hadcoins_bought = had_coins * usd_to_hadcoins;
        equity_hadcoins[investor] -= had_coins;
        equity_usd[investor] += equity_hadcoins[investor] / usd_to_hadcoins;
        total_hadcoins_bought -= had_coins;
    }
}