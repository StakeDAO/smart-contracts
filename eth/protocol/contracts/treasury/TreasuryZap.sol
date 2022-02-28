// SPDX-License-Identifier: AGPL
pragma solidity =0.6.12;

import "../temp/openzeppelin/IERC20.sol";
import "../temp/openzeppelin/SafeMath.sol";
import "../temp/openzeppelin/Address.sol";
import "../temp/openzeppelin/SafeERC20.sol";
import "../temp/openzeppelin/Ownable.sol";


interface CurveRegistry {
    function get_pool_from_lp_token(address) external view returns (address);
}

interface Uniswap {
    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts);

    function addLiquidity(
        address tokenA,
        address tokenB,
        uint256 amountADesired,
        uint256 amountBDesired,
        uint256 amountAMin,
        uint256 amountBMin,
        address to,
        uint256 deadline
    )
        external
        returns (
            uint256 amountA,
            uint256 amountB,
            uint256 liquidity
        );

    function getAmountsOut(uint256 amountIn, address[] memory path)
        external
        view
        returns (uint256[] memory amounts);
}

interface Zapper {
    function ZapOut(
        address payable toWhomToIssue,
        address swapAddress,
        uint256 incomingCrv,
        address toToken,
        uint256 minToTokens
    ) external returns (uint256 ToTokensBought);
}

contract TreasuryZap is Ownable {
    using SafeERC20 for IERC20;
    using Address for address;
    using SafeMath for uint256;

    uint256 public minAmount;

    address constant weth = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    address constant uniswap = 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D;
    address constant curve_registry = 0x7D86446dDb609eD0F5f8684AcF30380a356b2B4c;
    address constant curve_zap_out = 0xA3061Cf6aC1423c6F40917AD49602cBA187181Dc;
    mapping(address => address) curve_deposit;

    constructor() public {
        curve_deposit[0x845838DF265Dcd2c412A1Dc9e959c7d08537f8a2] = 0xeB21209ae4C2c9FF2a86ACA31E123764A3B6Bc06; // compound
        curve_deposit[0x9fC689CCaDa600B6DF723D9E47D84d76664a1F23] = 0xac795D2c97e60DF6a99ff1c814727302fD747a80; // usdt
        curve_deposit[0xdF5e0e81Dff6FAF3A7e52BA697820c5e32D806A8] = 0xbBC81d23Ea2c3ec7e56D39296F0cbB648873a5d3; // y
        curve_deposit[0x3B3Ac5386837Dc563660FB6a0937DFAa5924333B] = 0xb6c057591E073249F2D9D88Ba59a46CFC9B59EdB; // busd
        curve_deposit[0xC25a3A3b969415c80451098fa907EC722572917F] = 0xFCBa3E75865d2d561BE8D220616520c171F12851; // susdv2
        curve_deposit[0xD905e2eaeBe188fc92179b6350807D8bd91Db0D8] = 0xA50cCc70b6a011CffDdf45057E39679379187287; // pax
    }

    function setMinAmount(uint256 _minAmount) external onlyOwner {
        minAmount = _minAmount;
    }

    function swap(
        address token_in,
        address token_out,
        uint256 amount_in
    ) public returns (uint256 amount_out) {
        IERC20(token_in).safeTransferFrom(msg.sender, address(this), amount_in);
        address pool_in = token_to_curve_pool(token_in);
        if (pool_in != address(0)) {
            amount_out = swap_curve(token_in, token_out, amount_in);
        } else {
            amount_out = swap_uniswap(token_in, token_out, amount_in);
        }
    }

    function token_to_curve_pool(address token_in)
        internal
        returns (address pool)
    {
        pool = CurveRegistry(curve_registry).get_pool_from_lp_token(token_in);
        if (curve_deposit[token_in] != address(0))
            pool = curve_deposit[token_in];
    }

    function swap_curve(
        address token_in,
        address token_out,
        uint256 amount_in
    ) public returns (uint256 amount_out) {
        IERC20(token_in).safeApprove(curve_zap_out, amount_in);
        address pool_in = token_to_curve_pool(token_in);
        amount_out = Zapper(curve_zap_out).ZapOut(
            payable(msg.sender),
            pool_in,
            amount_in,
            token_out,
            0
        );
    }

    function swap_uniswap(
        address token_in,
        address token_out,
        uint256 amount_in
    ) public returns (uint256 amount_out) {
        if (token_in == token_out) return amount_in;
        bool is_weth = token_in == weth || token_out == weth;
        address[] memory path = new address[](is_weth ? 2 : 3);
        path[0] = token_in;
        if (is_weth) {
            path[1] = token_out;
        } else {
            path[1] = weth;
            path[2] = token_out;
        }
        if (IERC20(token_in).allowance(address(this), uniswap) < amount_in)
            IERC20(token_in).safeApprove(uniswap, type(uint256).max);
        uint256[] memory amounts = Uniswap(uniswap).swapExactTokensForTokens(
            amount_in,
            minAmount,
            path,
            msg.sender,
            block.timestamp
        );
        amount_out = amounts[amounts.length - 1];
    }
}
