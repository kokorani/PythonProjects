from datetime import datetime
import os
import shutil
#import mailservice as ms


date_today = datetime.today().strftime('%Y%m%d')
incoming_files_path = f"/Users/konchitagorani/Documents/Python Scripts/NamasteKart/incoming_files/{date_today}"
rejected_files_path=f"/Users/konchitagorani/Documents/Python Scripts/NamasteKart/rejected_files/{date_today}"
success_files_path=f"/Users/konchitagorani/Documents/Python Scripts/NamasteKart/success_files/{date_today}"
#email_date=datetime.date.today().strftime('%Y%m%d')
#subject=f"Validation email for {email_date}"

incoming_files = os.listdir(incoming_files_path)
total_cnt = len(incoming_files)

if(total_cnt)>0:
    success_cnt=0
    rejected_cnt=0
    for file in incoming_files:
        flag = True
        header = False
        file_path=os.path.join(incoming_files_path,file)
        with open(file_path,'r') as f:
            orders = f.readlines()[1:]

            if len(orders)>0:
                for order in orders:

                    rejected_reason=''
                    pid_reject_reason=''
                    empty_reject_reason=''
                    date_reject_reason=''
                    city_reject_reason=''
                    sales_reject_reason=''
                    order_dict={}

                    data_row = order.split(",")
                    order_dict['order_id']=data_row[0]
                    order_dict['order_date']=data_row[1]
                    order_dict['product_id']=data_row[2]
                    order_dict['quantity']=data_row[3]
                    order_dict['sales']=data_row[4]
                    order_dict['city']=data_row[5].strip()

                    def get_product_dict():
                        product_dict={}
                        product_file_path=r"/Users/konchitagorani/Documents/Python Scripts/product_master.csv"
                        with open(product_file_path) as f:
                            products = f.readlines()[1:]
                            for product in products:
                                product_dict[product.split(",")[0]] = product.split(',')[2]
                            
                            return product_dict
                        
                    def validate_product_id(id, products):
                        if id in products:
                            return True
                        else:
                            return False
                        
                    def validate_sales(order):
                        product_dict = get_product_dict()
                        if order['product_id'] in product_dict.keys():
                            return int(product_dict[order['product_id']])*int(order['quantity']) == int(order['sales'])
                        
                    def validate_order_date(date):
                          dt = datetime.strptime(date, '%Y-%m-%d').date()  # Use datetime directly
                          today_date = datetime.today().strftime('%Y%m%d')  # Use datetime directly
                          delta = (datetime.strptime(today_date, '%Y%m%d').date() - dt).days  # Compare dates
                          if delta >= 0:
                                return True
                          return False
                    
                    def validate_emptiness(orders):
                        empty_cols=[]
                        for k,v in orders.items():
                            if not orders[k] or orders[k] == '':
                                 empty_cols.append(k)
                        return empty_cols

                    
                    def validate_city(city):
                        if city in ['Mumbai','Bangalore']:
                            return True
                        return False
                    
                    def read_masterdata():
                        product_list=[]
                        product_file_path=r"/Users/konchitagorani/Documents/Python Scripts/product_master.csv"
                        with open(product_file_path) as f:
                            products = f.readlines()[1:]
                            for product in products:
                                product_list.append(product.split(',')[0])
                            return product_list
                        
                    products = read_masterdata()

                    
                    val_pid = validate_product_id(order_dict['product_id'], products)
                    val_od = validate_order_date(order_dict['order_date'])
                    val_city = validate_city(order_dict['city'])
                    val_empty = validate_emptiness(order_dict)
                    val_sales = validate_sales(order_dict)

                    if val_pid == False:
                        pid_reject_reason=f"Invalid product id {order_dict['product_id']}"
                        rejected_reason= rejected_reason + pid_reject_reason + ';'
                    if len(val_empty)>0:
                        for col in val_empty:
                                empty_reject_reason = empty_reject_reason + col + ','
                                empty_reject_reason = 'Columns ' + empty_reject_reason.strip(',') + ' are empty.'
                                rejected_reason = rejected_reason + empty_reject_reason + ';'
                    if not val_od:
                                date_reject_reason = f"Date {order_dict['order_date']} is a future date."
                                rejected_reason = rejected_reason + date_reject_reason + ';'
                    if not val_city:
                                city_reject_reason = f"Invalid city {order_dict['city']}."
                                rejected_reason = rejected_reason + city_reject_reason + ';'
                    if not val_sales and val_pid:
                                sales_reject_reason = f'Invalid Sales calculation.'
                                rejected_reason = rejected_reason + sales_reject_reason

                    if val_pid and val_od and val_city and len(val_empty) == 0 and val_sales:
                        continue
                    else:
                        row_str=''
                        flag=False
                        if not os.path.exists(f'{rejected_files_path}'):
                            os.makedirs(f'{rejected_files_path}', exist_ok=True)
                        shutil.copy(f'{incoming_files_path}/{file}', f'{rejected_files_path}/{file}')
                        rejected_cnt += 1
                        with open(f'{rejected_files_path}/error_{file}', 'a') as f:
                            for key in order_dict.keys():
                                row_str = row_str + order_dict[key] + ','
                            row_str = row_str + rejected_reason
                            row_str = row_str.strip(',')
                            if not header:
                                f.write('order_id,order_date,product_id,quantity,sales,city,rejected_reason')
                                f.write('\n')
                                header = True
                            f.write(row_str)
                            f.write('\n')
                            f.close()
                else:
                    if flag:
                        if not os.path.exists(f'{success_files_path}'):
                            os.makedirs(f'{success_files_path}', exist_ok=True)
                        shutil.copy(f'{incoming_files_path}/{file}', f'{success_files_path}/{file}')
                        success_cnt += 1

            else:
                if not os.path.exists(f'{rejected_files_path}'):
                    os.makedirs(f'{rejected_files_path}', exist_ok=True)
                shutil.copy(f'{incoming_files_path}/{file}', f'{rejected_files_path}/{file}')

                with open(f'{rejected_files_path}/error_{file}', 'a') as f:
                    f.write("Empty file")
                    f.close()
                rejected_cnt += 1
    else:
        body = f"""
        Total Files: {total_cnt} \n
        Successful Files: {success_cnt} \n
        Rejected Files: {rejected_cnt}
        """
        #ms.sendmail(subject, body)
#else:
    #ms.sendmail(subject, "No file present in source folder.")

