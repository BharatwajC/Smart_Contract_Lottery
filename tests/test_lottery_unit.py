#06/02  price $3017.64
#0.0165692395381822
#1600000000000000    16zeroes + 2nonzero      1eth = 10 **18 wei
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENT,get_account,fund_with_link, get_contract
from brownie import Lottery,accounts,config,network,exceptions
from web3 import Web3
from scripts.deploy import deploy_lottery
import pytest


def test_get_entrance_fee():

    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENT:       # we want to only test it in developmental environment
        pytest.skip()

    #Arrange
    lottery = deploy_lottery()
    
    #Act
    
    
    #helpful scripts is gonna deploy these mocks
    #so deploy mocks we need initial value
    # which in our case was 1eth = 2000usd
    # 2000 eth/usd
    #usdEntryfee is 50
    # 2000/1 == 50/x === 0.025      (50/2000)
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()
    
    #Assert

    assert expected_entrance_fee == entrance_fee  #brownie test -k test_get_entrance_fee

def test_cant_enter_unless_starter():
    #Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENT:       # we want to only test it in developmental environment
        pytest.skip() 

    #Act/Assert
    lottery = deploy_lottery()  
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from":get_account(),"value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
    #Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENT:       # we want to only test it in developmental environment
        pytest.skip() 

    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})

    #Act
    lottery.enter({"from":account, "value": lottery.getEntranceFee()})    

    #Assert 
    assert lottery.players(0) == account       # check out lottery.sol enter() you can understand  players.push(msg.sender)

def test_can_end_lottery():
    #Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENT:       # we want to only test it in developmental environment
        pytest.skip() 

    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from":account, "value": lottery.getEntranceFee()}) 
    fund_with_link(lottery)
    lottery.endLottery({"from": account}) 

    assert lottery.lottery_state() == 2             #CALCULATING_WINNER is in the position 2 in gthe enum LOTTERY_STATE 


def test_can_pick_winner_correctly():
    #Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENT:       # we want to only test it in developmental environment
        pytest.skip() 

    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from":account, "value": lottery.getEntranceFee()}) 
    lottery.enter({"from":get_account(index = 1), "value": lottery.getEntranceFee()})
    lottery.enter({"from":get_account(index = 2), "value": lottery.getEntranceFee()})     
    fund_with_link(lottery)

    # Now VRFCoordinatorMock has gunction callBackWithRandomness which calls rawFulfillRandimness which
    #eventually call rawFullfillRandomness which call fullFillRandomness
    
    #Now we have to pretend to be a chainlink node to call this callBackWithRandomness function

    #Events:
    # events are pieces of data executed in blockchain stored in the blockchain chain but are not accessible by any smart contracts
    # they are kind off the print line of the blockchain otr print statement of the blockchain
    # events are much more gas efficient than using a storage variable

    transaction = lottery.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    # events are very helpful upgrading smart contract, understanding mapping
    STATIC_RNG = 777        # our static random number

    get_contract("vrf_coordinator").callBackWithRandomness(request_id, STATIC_RNG, lottery.address, {"from": account})  # since we are making state change
    # manually acting as a chainlink node basically dummying the chainlink node


    #777%3 = 0 which implies our account is gonna be the winner     account[0]
    
    starting_balance_account = account.balance()     # account[0] is going to be the winner 777%3    reason for 3 is number of participants = 3 in iur case
    balance_of_lottery = lottery.balance()
    
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_account + balance_of_lottery
























#Initial test_lottery before introduction to unit and integration testing


# def test_get_entrance_fee():
#     account = accounts[0]
#     lottery = Lottery.deploy(
#         config["networks"][network.show_active()]["eth_usd_price_feed"],
#         {"from":account})
#     #assert lottery.getEntranceFee()  >  Web3.toWei(0.015, "ether")          #1500000000000000
#     #assert lottery.getEntranceFee()  <  Web3.toWei(0.020, "ether")
    

    
    # Unit Tests:
    # A way of testing the smallest pieces of code in an isolated instance
    # so unit test on a development environment

    # Integration Tests:
    # A way of testing across multiple complex systems
    # similarlly Integration test with Testnets
    
