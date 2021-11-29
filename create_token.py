from solcx import install_solc
from solcx import compile_source
from web3 import Web3
import json

install_solc(version='0.7.0')

import solcx

"""
    Symbol – N47
    Name – N47Token
    Decimals – 0
    Total Supply – 1000000
"""
    



solid = """
// SPDX-License-Identifier: unlicensed
pragma solidity 0.7.0;
// ----------------------------------------------------------------------------
// Safe maths
// ----------------------------------------------------------------------------

// ----------------------------------------------------------------------------
// ERC Token Standard #20 Interface
// https://github.com/ethereum/EIPs/blob/master/EIPS/eip-20.md
// ----------------------------------------------------------------------------
abstract contract ERC20Interface {
    function totalSupply() virtual public view returns (uint);
    function balanceOf(address tokenOwner) virtual public view returns (uint balance);
    function allowance(address tokenOwner, address spender) virtual public view returns (uint remaining);
    function transfer(address to, uint tokens) virtual public returns (bool success);
    function approve(address spender, uint tokens) virtual public returns (bool success);
    function transferFrom(address from, address to, uint tokens) virtual public returns (bool success);
    event Transfer(address indexed from, address indexed to, uint tokens);
    event Approval(address indexed tokenOwner, address indexed spender, uint tokens);
}
// ----------------------------------------------------------------------------
// ERC20 Token, with the addition of symbol, name and decimals
// assisted token transfers
// ----------------------------------------------------------------------------
contract name_here is ERC20Interface {
    string public symbol;
    string public  name;
    uint8 public decimals;
    uint public _totalSupply;
    mapping(address => uint) balances;
    mapping(address => mapping(address => uint)) allowed;
    // ------------------------------------------------------------------------
    // Constructor
    function safeAdd(uint a, uint b) public pure returns (uint c) {
        c = a + b;
        require(c >= a);
    }
    function safeSub(uint a, uint b) public pure returns (uint c) {
        require(b <= a);
        c = a - b;
    }
    // ------------------------------------------------------------------------
    constructor() {
        symbol = "symbol_here";
        name = "name_here";
        decimals = 0;
        _totalSupply = supply_here;
        balances[msg.sender] = _totalSupply;
        emit Transfer(address(0), msg.sender, _totalSupply);
    }
    // ------------------------------------------------------------------------
    // Total supply
    // ------------------------------------------------------------------------
    function totalSupply() public override view returns (uint) {
        return _totalSupply - balances[address(0)];
    }
    
    function get_symbol() public view returns (string memory) {
        return symbol;
    }

    function get_name() public view returns (string memory) {
        return name;
    }
    

    // ------------------------------------------------------------------------
    // Get the token balance for account tokenOwner
    // ------------------------------------------------------------------------
    function balanceOf(address tokenOwner) public override view returns (uint balance) {
        return balances[tokenOwner];
    }
    // ------------------------------------------------------------------------
    // Transfer the balance from token owner's account to receiver account
    // - Owner's account must have sufficient balance to transfer
    // - 0 value transfers are allowed
    // ------------------------------------------------------------------------
    function transfer(address receiver, uint tokens) public override returns (bool success) {
        balances[msg.sender] = safeSub(balances[msg.sender], tokens);
        balances[receiver] = safeAdd(balances[receiver], tokens);
        emit Transfer(msg.sender, receiver, tokens);
        return true;
    }
    // ------------------------------------------------------------------------
    // Token owner can approve for spender to transferFrom(...) tokens
    // from the token owner's account
    //
    // https://github.com/ethereum/EIPs/blob/master/EIPS/eip-20.md
    // recommends that there are no checks for the approval double-spend attack
    // as this should be implemented in user interfaces 
    // ------------------------------------------------------------------------
    function approve(address spender, uint tokens) public override returns (bool success) {
        allowed[msg.sender][spender] = tokens;
        emit Approval(msg.sender, spender, tokens);
        return true;
    }
    // ------------------------------------------------------------------------
    // Transfer tokens from sender account to receiver account
    // 
    // The calling account must already have sufficient tokens approve(...)-d
    // for spending from sender account and
    // - From account must have sufficient balance to transfer
    // - Spender must have sufficient allowance to transfer
    // - 0 value transfers are allowed
    // ------------------------------------------------------------------------
    function transferFrom(address sender, address receiver, uint tokens) public override returns (bool success) {
        balances[sender] = safeSub(balances[sender], tokens);
        allowed[sender][msg.sender] = safeSub(allowed[sender][msg.sender], tokens);
        balances[receiver] = safeAdd(balances[receiver], tokens);
        emit Transfer(sender, receiver, tokens);
        return true;
    }
    // ------------------------------------------------------------------------
    // Returns the amount of tokens approved by the owner that can be
    // transferred to the spender's account
    // ------------------------------------------------------------------------
    function allowance(address tokenOwner, address spender) public override view returns (uint remaining) {
        return allowed[tokenOwner][spender];
    }
}
   """

theta_network = "https://eth-rpc-api.thetatoken.org/rpc"


def create_contract(symbol,name, supply,address):
    global solid 
    
    solid = solid.replace("symbol_here",symbol)
    solid = solid.replace("name_here",name)
    if supply is not str:
        solid = solid.replace("supply_here",str(supply))
    else:
        solid = solid.replace("supply_here",supply)
    
    w3 = Web3(Web3.HTTPProvider(theta_network))
    
    
    w3.eth.default_account = address
    
    compiled_sol = solcx.compile_source(
        solid,
        output_values=["abi", "bin-runtime","bin"],
        solc_version="0.7.0")
    
    # retrieve the contract interface
    contract_id, contract_interface = compiled_sol.popitem()
    
    # get bytecode / bin
    bytecode = contract_interface['bin']
    
    
    #get abi
    abi = contract_interface['abi']
    
    Greeter = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Submit the transaction that deploys the contract
    tx_hash = Greeter.constructor().transact()
    
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    
    return tx_receipt.contractAddress


