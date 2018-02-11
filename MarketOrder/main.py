#!/bin/python3

import os
import sys
import operator
from datetime import datetime

output = []
# Complete the function below.
class Order:
    def __init__(self, q):
        self.order_id = int(q[1])
        self.timestamp = int(q[2])
        self.symbol = q[3]
        self.order_type = q[4][0] # M - Market, L-Limt, I-IOC
        self.side = q[5] # B - Buy , S - Sell
        self.price = float(q[6])
        self.quantity = int(q[7])
        self.closed = False
        self.matched = False
        self.cancled = False
class MatchBook:
    buy_sell_match = []
    def __init__(self, symbol):
        self.symbol = symbol
        self.buy_order = {}
        self.sell_order = {}
    
    
    def state(self):
        sort_price = []
        for order in sorted(self.buy_order.values(), key=operator.attrgetter('timestamp')):
            sort_price.append(order)
        sort_price.sort(key=operator.attrgetter('price'), reverse=True)
        for order in sort_price:
            print(self.buy_string(order))
        for key in self.buy_order:
            order = self.buy_order[key]
            #self.buy_sell_match.append(order.symbol + '|' + self.buy_string(order))
        for item in self.buy_sell_match:
            print_output(item)
    def buy_string(self, order):
        return str(order.order_id) +',' + str(order.order_type) +',' + str(order.quantity) + ',' + str(order.price) 
    def sell_string(self, order):
        return str(order.price) +',' + str(order.quantity) +',' + order.order_type + ',' + str(order.order_id)
    def add(self, order):
        if order.side == 'B':
            print("Buy" + order.symbol)
            self.buy_order[order.order_id] = order
        elif order.side == 'S':
            print("SELL" + order.symbol)            
            self.sell_order[order.order_id] = order

    
class MatchEngine:

    last_order_timestamp = 0
    order_book = {}
    def new(self, command):
        q = command.split(',')
        if len(q) == 8:
            try:
                order = Order(q)
                if order.timestamp >= self.last_order_timestamp:
                    self.order_book[order.order_id] = order
                    self.last_order_timestamp = order.timestamp
                    print_output(q[1] + ' - Accept')
                else:
                    print_output(q[1] + ' - Reject - 303 - Invalid order details')
            except:
                print_output(q[1] + ' - Reject - 303 - Invalid order details')
                print_output(sys.exc_info())
    def amend(self, command):
        q = command.split(',')
        if len(q) == 8:
            try:
                amend_order = Order(q)
                if amend_order.timestamp >= self.last_order_timestamp:                
                    if amend_order.order_id in self.order_book:
                        #Validate Amend order
                        old_order = self.order_book[amend_order.order_id]
                        if ((amend_order.order_type != old_order.order_type) or
                            (amend_order.side != old_order.side) or
                            (amend_order.symbol != old_order.symbol) or 
                            old_order.matched or old_order.cancled or old_order.closed):
                            print_output(q[1] + ' - AmendReject - 101 - Invalid amendment details')
                        else:
                            if amend_order.price == self.order_book[amend_order.order_id].price:
                                #Do not update priority 
                                if amend_order.quantity <= self.order_book[amend_order.order_id].quantity:
                                    #If the quantity in the amend request is less than or equal to the 
                                    #currently matched quantity, then order should be considered closed
                                    print_output(q[1] + ' - AmendReject - 101 - Invalid amendment details')
                                    
                                else:
                                    self.order_book[amend_order.order_id].quantity = amend_order.quantity
                                    self.last_order_timestamp = amend_order.timestamp
                                    print_output(q[1] + ' - AmendAccept')                                
                            else:
                                old_order.price = amend_order.price
                                old_order.timestamp = amend_order.price
                                old_order.quantity = amend_order.quantity
                                self.last_order_timestamp = amend_order.timestamp
                                print_output(q[1] + ' - AmendAccept')
                                
                    else:
                        print_output(q[1] + ' - AmendReject - 404 - Order does not exist')
                else:
                    print_output(q[1] + ' - AmendReject - 101 - Invalid amendment details')
                                       
            except:
                print_output(q[1] + ' - AmendReject - 101 - Invalid amendment details')
        else:
            print_output(q[1] + ' - AmendReject - 101 - Invalid amendment details')
    
    def cancel(self, command):
        q = command.split(',')
        if len(q) >= 3:
            try:
                
                cancel_order_id = int(q[1])
                cancel_order_timestamp = int(q[2])
                if cancel_order_timestamp >= self.last_order_timestamp:
                    if cancel_order_id in self.order_book:
                        old_order = self.order_book[cancel_order_id]
                        if not old_order.cancled and not old_order.matched:
                            old_order.cancled = True
                            print_output(q[1] + ' - CancelAccept')
                        else:
                            print_output(q[1] + ' - CancelReject - 404 - Order does not exist')
                    else:
                        print_output(q[1] + ' - CancelReject - 404 - Order does not exist')
                else:
                    print_output(q[1] + ' - CancelReject - 404 - Order does not exist')
            except:
                print_output(q[1] + ' - CancelReject - 404 - Order does not exist')
        else:
            debug_print("")            
    def match(self, command):
        q = command.split(',')
        if q.length == 8:
            try:
                order = Order(q)
            except:
                print_output(q[1] + ' - Reject - 303 - Invalid order details')
    def query(self, command):
        q = command.split(',')
        dict_match_book = {}
        list_symbol = []
        for key in self.order_book:
            order = self.order_book[key]
            if order.symbol in dict_match_book:
                #print("old = " + order.symbol)
                dict_match_book[order.symbol].add(order)
            else:
                print("Neq = "+order.symbol)
                dict_match_book[order.symbol] = MatchBook(order.symbol)
                dict_match_book[order.symbol].add(order)
                list_symbol.append(order.symbol)
        list_symbol.sort()
        for symbol in list_symbol:
            #print(str(symbol))
            dict_match_book[symbol].state()

    
    def market_buy(self):
        #Market Buy: Amount x, where x is current lowest selling price available in the order book.
        return False
    def market_sell(self):
        #Market Buy: Amount x, where x is current highest buying price available in the order book.
        return False

    def limit_buy(self):
        #Limit Buy: Amount , where x is selling price and x <= p, eventually.
        return False
    def limit_sell(self):
        #Limit Sell: Amount , where x is buying price and x >= p, eventually.
        return False

    def ioc_buy(self):
        #IOC Limit Buy: Amount , where x is selling price and x <= p, now.
        return False
    def ioc_sell(self):
        #IOC Limit Sell: Amount , where x is buying price and x >= p, now.
        return False
def print_output(msg):
        output.append(msg)
        print(msg)
def debug_print(msg):
    print(msg)
def processQueries(queries):
    # Write your code here.
    #queries
    engine = MatchEngine()
    for q in queries:
        command = q[0]
        if command == 'N':
            engine.new(q)
        elif command == 'A':
            engine.amend(q)
        elif command == 'X':
            engine.cancel(q)
        elif command == 'M':
            engine.match(q)
        elif command == 'Q':
            engine.query(q)
        
        else:
            print('COMMAND NOT FOUND')
    
    return output


if __name__ == '__main__':

    #f = open(os.environ['OUTPUT_PATH'], 'w')
    f = open('output.txt', 'w')
    #queries_size = int(input())
    fint = open('input.txt','r')
    queries_size = int(fint.readline())

    queries = []
    for _ in range(queries_size):
        #queries_item = input()
        queries_item = fint.readline()
        
        queries.append(queries_item)

    response = processQueries(queries)

    f.write('\n'.join(response))

    f.write('\n')

    f.close()
    fint.close()