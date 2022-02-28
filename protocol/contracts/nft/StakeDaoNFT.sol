//SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.5.0;

import "./ERC1155Tradable.sol";

/**
 * @title Stake Dao NFT Contract
 */
contract StakeDaoNFT is ERC1155Tradable {
    constructor(address _proxyRegistryAddress)
        public
        ERC1155Tradable("Stake DAO NFT", "sdNFT", _proxyRegistryAddress)
    {
        _setBaseMetadataURI(
            "https://gateway.pinata.cloud/ipfs/QmZwsoGKw42DxNwnQXKtWiuULSzFrUPCNHUx6yhNgrUMj6/metadata/"
        );
    }

    function contractURI() public view returns (string memory) {
        return
            "https://gateway.pinata.cloud/ipfs/Qmc1i37KPdg7Cp8rzjgp3QoCECaEbfoSymCpKG8hF85ENv";
    }
}
