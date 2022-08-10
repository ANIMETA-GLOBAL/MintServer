// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

import "@openzeppelin/contracts/token/ERC1155/extensions/ERC1155URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract ANIMETA is ERC1155URIStorage, Ownable {
    event mintTo(address indexed  minter,address indexed  owner, uint tokenId,uint amount,string tokenUri);
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIdCounter;
    constructor() ERC1155("ANIMETA") {}

    function mint(address account, uint256 amount, bytes memory data, string memory uri)
        public
        onlyOwner
    {
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();
        _mint(account, tokenId, amount, data);
        _setURI(tokenId,uri);
        emit mintTo(msg.sender,account,tokenId,amount,uri);
    }

    function setTokenUri(uint tokenId,string memory uri) public onlyOwner {
        _setURI(tokenId,uri);
    }

}