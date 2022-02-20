from brownie import Contract, accounts,config,network,MockV3Aggregator,VRFCoordinatorMock,LinkToken,interface
from web3 import Web3


LOCAL_BLOCKCHAIN_ENVIRONMENT = ["development", "ganache-local"]
FORKED_LOCAL_ENVIRONMENT = ["mainnet-fork","mainnet-fork-dev"]

def get_account(index=None, id=None):

    #   accounts[0]
    # account.add("env")
    # account.load("id")
    if index:
        return accounts[index]

    if id:
        return accounts.load(id)

    if(network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENT or network.show_active() in FORKED_LOCAL_ENVIRONMENT):     #If the network is developmental
        return accounts[0]
                                               #If the network is testnet
    return accounts.add(config["wallets"]["from_key"])   


contract_to_mock = {

    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken

}

def get_contract(contract_name):            
    """ This function will grab the contract addresses from the brownie config
        if defined, otherwise, it will deploy a mock version of that contract, 
        and return the mock contract.

        Args:
            contract_name(string)
        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed version
            of this contract.

            eg:
            Mockv3Aggregator[-1]

    """
    contract_type = contract_to_mock[contract_name]
    # we dont need to deploy mock on fork_local_environment
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENT:       #Development 
        if len(contract_type) <= 0:
            # the above statement is equivalnet of doing ,ockV3Aggregator.length (how many MockV3Aggrgator have been deployed)
            deploy_mocks()

    # This is same as what we done in brownie fund me
    # now to get that mock get that contract
        contract = contract_type[-1]        # equivalent to MockV3ggregator[-1]


    else:
        contract_address = config["networks"][network.show_active()][contract_name]     #contract_name  could be price_feed 
        #two things we need is
        #address
        #ABI        we already got ABI from our MockV3Aggrgator ;  we gor the address from the contract_address

        contract = Contract.from_abi(contract_type._name, contract_address, contract_type.abi)        #allows us to get contract from abi and its address
        #MockV3Affregator.abi gives us abi
        #mock contract has all the function of regular contract

    return contract     # gonna return the contract


DECIMALS = 8
INITIAL_VALUE = 2000_00000000       # 2000 folllowed by 8 zeroes

def deploy_mocks(decimals = DECIMALS, initial_value = INITIAL_VALUE):
    account = get_account()    
    # mock_price_feed = MockV3Aggregator.deploy(
    #     decimals, initial_value, {"from:account"}
    # )

    MockV3Aggregator.deploy( decimals, initial_value, {"from" :account} )
    link_token = LinkToken.deploy({"from":account})      #check the constructor to pass which parameter 
    VRFCoordinatorMock.deploy( link_token.address, {"from": account})
    
    
    print("Deployed")


def fund_with_link(contract_address, account = None, link_token=None, amount = 10000000000_0000000):     # 0.1LINK default amount
   
    account = account if account else get_account()                     # if account parameter does not exist then execute get_account()
    link_token = link_token if link_token else get_contract("link_token")
    
    tx = link_token.transfer(contract_address, amount, {"from":account})
    
    #link_token_contract = interface.LinkTokenInterface(link_token.address)      #instead of abi Contract.abi in above case this is just another way


    #If you have interface brownie is smart enough to compile down from abi itself 
    #tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Fund contract!")
    return tx