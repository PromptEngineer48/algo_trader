import streamlit as st
# Display the Page Title
st.title('🦜️🔗 Automatic Trader')

prompt = st.text_input("type yes to start the show")

if prompt:
    from py5paisa import FivePaisaClient
    from py5paisa.order import Order, OrderType, Exchange
    from py5paisa.strategy import *
    from datetime import datetime, timedelta, time
    import json
    import threading
    import pandas as pd
    from time import sleep
    import random

    def connect():
        global client
        cred = {
            "APP_NAME": "5P52252457",
            "APP_SOURCE": "15132",
            "USER_ID": "pyb6U48ghXF",
            "PASSWORD": "JId8j0zHzmN",
            "USER_KEY": "7MjEZ6I6VXfhNGqWi6McJ41NgzRlQn5C",
            "ENCRYPTION_KEY": "1W85rnZDjXDxyYKysfcHdEo5NiMMa8gn"
        }

        try:
            client = FivePaisaClient(email="palash14.india@gmail.com", passwd="A1b2c3d4@5", dob="19921103", cred=cred)
            client.login()
        except Exception as e:
            print("Some error in connection =>", e)


    def ltp(script):
        # global ltp_value
        req_list = [
            {"Exch": "N", "ExchType": "C", "ScripCode": script},
        ]

        req_data = client.Request_Feed('mf', 's', req_list)

        def on_message(ws, message):
            global ltp_value
            text = message
            data = json.loads(text)
            for d in data:
                if "LastRate" in d:
                    ltp_value = d["LastRate"]
                    # print(ltp_value)
                    return ltp_value
                    
                    # check_heikin_ashi_bars(script)

        client.connect(req_data)
        t = threading.Thread(target=client.receive_data, args=(on_message,))
        t.start()
        t.join(timeout=5)  # Wait for the thread to finish or timeout after 5 seconds
        return ltp_value


    def create_order(client, OrderType='B', ScripCode = 50557, Qty = 50, Price = 0, strike_price = 18000, ce_or_pe = 'CE'):
        client.place_order(OrderType=OrderType,Exchange='N',ExchangeType='D', ScripCode = ScripCode, Qty=Qty, Price=Price)

        strike_price = strike_price
        # Erase the contents of the file before writing
        with open('order_details.txt', 'w+') as file:
            file.write(f"Script Code: {ScripCode}\n")
            file.write(f"Quantity: {Qty}\n")
            file.write(f"Strike Price: {strike_price}\n")
            file.write(f"CE_or_PE: {ce_or_pe}\n")
        sleep(4)

    def extract_script_code(name):
        # Split the name by whitespace
        name_parts = name.split()
        # Get the script code from the last part
        script_code = name_parts[-1]
        return script_code


    def main():
        # print("Starting Sequence")
        connect()

        # Read the order details from the file
        st.write("Reading the Order Details from the file")
        try:
            with open('order_details.txt', 'r') as file:
                order_details = file.readlines()

            # Get the script code and quantity from the order details
            script_code = None
            quantity = None
            for line in order_details:
                if line.startswith("Script Code"):
                    script_code = line.split(":")[-1].strip()
                elif line.startswith("Quantity"):
                    quantity = line.split(":")[-1].strip()
                elif line.startswith("Strike Price"):
                    strike_price = line.split(":")[-1].strip()
                elif line.startswith("CE_or_PE"):
                    ce_or_pe = line.split(":")[-1].strip()

            print('\nscript_code: ', script_code)
            print('quantity: ', quantity)
            print('strike_price: ', strike_price)
            print('ce_or_pe: ', ce_or_pe, "\n")
            
            st.write('script_code: ', script_code)
            st.write('quantity: ', quantity)
            st.write('strike_price: ', strike_price)
            st.write('ce_or_pe: ', ce_or_pe, "\n")
        
        except Exception as e:
            print("Script and Order Not found")

        ## If the script and quantity found in file
        if script_code and quantity:
            # Convert the script code to an integer
            script_code = int(script_code)
            # Check for Open Positions
            # 
            positions = client.positions()
            # positions = [{'BodQty': 150, 'BookedPL': 0, 'BuyAvgRate': 186.19, 'BuyQty': 150, 'BuyValue': 27928.5, 'Exch': 'N', 'ExchType': 'D', 'LTP': 143, 'MTOM': -6478.5, 'Multiplier': 1, 'NetQty': 150, 'OrderFor': 'D', 'PreviousClose': 181.45, 'ScripCode': 55357, 'ScripName': 'BANKNIFTY 15 Jun 2023 PE 43800.00', 'SellAvgRate': 0, 'SellQty': 0, 'SellValue': 0}, {'BodQty': 150, 'BookedPL': 0, 'BuyAvgRate': 116.25, 'BuyQty': 150, 'BuyValue': 17437.5, 'Exch': 'N', 'ExchType': 'D', 'LTP': 73.65, 'MTOM': -6390, 'Multiplier': 1, 'NetQty': 150, 'OrderFor': 'D', 'PreviousClose': 122.9, 'ScripCode': 55356, 'ScripName': 'BANKNIFTY 15 Jun 2023 CE 44500.00', 'SellAvgRate': 0, 'SellQty': 0, 'SellValue': 0}]

            # Search for the script code and quantity in the open positions
            for position in positions:
                if position['ScripCode'] == script_code:
                    net_quantity = position['NetQty']
                    if net_quantity >= int(quantity):
                        print("Script Code and Quantity found in open positions.")
                        st.write("Script Code and Quantity found in open positions.")
                     
                        ## Managment (use break to get out of the loop)
                        ## Essentially, once you enter the Management, its either normal stoploss or Trailing stoploss that will hit
                        ## Once stop loss hits, you clear the order_details.txt file and break
                        print("\n...Start the Management...")
                        st.write("..Start the Management...")

                        sleep(2)
                        # print("Management1")
                        ## Let's do the magic here.
                        ## compare the LTP and Strike Price
                        script = 999920000
                        LTP_manage = int(ltp(script))
                        strike_price_manage = int(strike_price)

                        print(LTP_manage, strike_price_manage)
                        
                        sl_points = 40

                        if ce_or_pe == "CE":
                            # Initialize the trigger price
                            trigger_price = strike_price_manage - sl_points

                            while True:
                                # Get the updated LTP_manage value
                                LTP_manage = int(ltp(script))

                                # Update the trigger price if the LTP_manage value is higher than the current trigger price
                                new_trigger_price = LTP_manage - sl_points
                                if new_trigger_price >= trigger_price:
                                    trigger_price = new_trigger_price
                                
                                print("\nPresenty in CE Management Loop waiting for SL Trigger\n")
                                print("Since LTP > Trigger Price", LTP_manage, trigger_price)

                                # Check if the trigger price has been reached for closing the position
                                if LTP_manage <= trigger_price:
                                    # Close the position
                                    # Your code to close the position goes here
                                    create_order(client, OrderType='S', ScripCode = int(script_code), Qty = quantity, Price = 0, strike_price = strike_price, ce_or_pe= ce_or_pe)

                                    print("Closing position at trigger price:", trigger_price)
                                    st.write("Closing position at trigger price from CE management loop:")

                                    print("clearing the contents (from CE management loop)\n")
                                    with open('order_details.txt', 'w') as file:
                                        pass  # This line clears the file

                                    break  # Exit the while loop and end the program


                        elif ce_or_pe == "PE":
                            # Initialize the trigger price
                            trigger_price = strike_price_manage + sl_points

                            while True:
                                # Get the updated LTP_manage value
                                LTP_manage = int(ltp(script))


                                new_trigger_price = LTP_manage + sl_points
                                if new_trigger_price <= trigger_price:
                                    trigger_price = new_trigger_price

                                print("\nPresenty in PE Management Loop waiting for SL Trigger\n")
                                print("Since LTP < Trigger Price", LTP_manage, trigger_price)

                                if LTP_manage >= trigger_price:
                                    # Close the position
                                    # Your code to close the position goes here
                                    create_order(client, OrderType='S', ScripCode = int(script_code), Qty = quantity, Price = 0, strike_price = strike_price, ce_or_pe= ce_or_pe)

                                    print("Closing position at trigger price:", trigger_price)
                                    st.write("Closing position at trigger price from PE management loop:")

                                    print("clearing the contents (from PE Management Loop)\n")
                                    with open('order_details.txt', 'w') as file:
                                        pass  # This line clears the file
                                    break  # Exit the while loop and end the program
                else:
                    print("Some major issues. Order was placed but not available in positions")
                    print("Pausing the code for manual checking")
                    sleep(25000)


        else:
            print("No entry in order_details.txt.")
            print("Creating Fresh Orders")

            script = 999920000 ## This is NIFTY
            # historian(script)
            # print("...Fetching LTP...")
            LTP = int(ltp(script))
            print("LTP", LTP)

            csv_file = "scripmaster-csv-format.csv"  #Read the CSV file
            df = pd.read_csv(csv_file, low_memory=False) #Read into dataframe

            ##################################################
            ## Bullish or Bearish Finding Code
            ## This code will decide your bias Bullish or bias
            ## And then return a variable called CE_or_PE as CE or PE


            ##################################################
            # Construct the name
            try: 
                instrument = "NIFTY"
                Qty = 100
                expiry_date = "15 Jun 2023"  ####### IMPORTANT CHANGE ######

                ce_count = 0
                pe_count = 0

                for _ in range(2000):
                    CE_or_PE = random.choice(["CE", "PE", "PE", "CE"])
                    if CE_or_PE == "CE":
                        ce_count += 1
                    else:
                        pe_count += 1
                
                print('\nce count:', ce_count)
                print('pe count:', pe_count)

                if ce_count > pe_count:
                    CE_or_PE = "CE"
                else:
                    CE_or_PE = "PE"


                # CE_or_PE = "PE"

                # ## Code for giving a 50 point ITM boost
                # if CE_or_PE == "PE":
                #     LTP = LTP + 50
                # else:
                #     LTP = LTP - 50

                remainder = LTP % 50
                if remainder <= 25:
                    strike_price = LTP - remainder
                else:
                    strike_price = LTP + (50 - remainder)

                name = instrument + " " + expiry_date + " " + CE_or_PE + " " + str(strike_price) + ".00"

                print("\nname: ", name)
                # name = "NIFTY 29 Jun 2023 CE 18000.00"
            except Exception as e:
                print('Cannot construct the name:', e)

            ##################################################
            # Get the Script code
            try:
                index_number = df[df['Name'] == name].index[0]
                scriptcode_value = df.loc[index_number, 'Scripcode']
                print("\nscript_code: ", scriptcode_value, "\n")
            except Exception as e:
                print('Cannot get the script code:', e)

            ##################################################
            # Place Order and Store the Scriptcode_value & quantity in a text file
            try:
                create_order(client, OrderType='B', ScripCode = int(scriptcode_value), Qty = Qty, Price = 0, strike_price = strike_price, ce_or_pe= CE_or_PE)

            except Exception as e:
                print('Cannot Place order', e)
            #https://www.5paisa.com/developerapi/order-request-place-order
            ##################################################
            

    if __name__ == '__main__':
        while True:
            st.write("Running Main Loop")
            main()
            sleep(5)



