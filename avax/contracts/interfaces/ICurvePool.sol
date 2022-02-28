// SPDX-License-Identifier: MIT
pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

interface ICurvePool {
  function add_liquidity(
    uint256[2] calldata amounts,
    uint256 min_mint_amount,
    bool use_underlying
  ) external returns (uint256);

  function add_liquidity(
    uint256[3] calldata amounts,
    uint256 min_mint_amount,
    bool use_underlying
  ) external returns (uint256);

  function add_liquidity(
    uint256[4] calldata amounts,
    uint256 min_mint_amount,
    bool use_underlying
  ) external returns (uint256);

  function add_liquidity(
    uint256[5] calldata amounts,
    uint256 min_mint_amount,
    bool use_underlying
  ) external returns (uint256);
}
