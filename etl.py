import logging
import pandas as pd
from pandas.io.json import json_normalize

from scripts import db_functions as db
from scripts import get
from scripts import Rental


def main():
    """Extract, Transform, Load"""

    logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info('Start')

    frames = []
    i = 0 #Loop counter

    while True:

        try:

            page = str(i)

            url = 'https://www.rentfaster.ca/api/search.json?keywords=&proximity_type=location-proximity&cur_page=' + page + '&beds=&type=&price_range_adv[from]=null&price_range_adv[to]=null&novacancy=0&city_id=1'

            # Access object
            scr = get.Accessor(url)

            data = scr.get_json()

            # There are multiple keys that can be accessed at this level, we want the listings data
            listings = data['listings']

            # We have reached the last page
            if len(listings) == 0:
                break
            
            # We have not reached the last page
            i += 1
                
            # Convert to a dataframe
            df = json_normalize(listings)

            # Append to the list of dataframes
            frames.append(df)

            logging.info("Page " + page + " data obtained")

        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            logging.info(message)
            raise

        finally:

            df = pd.concat(frames, axis=0)

            # Clean the data 
            # Square feet often has unessary characters combined with the numeric value
            df['sq_feet'].replace(regex=True,inplace=True,to_replace=r'\D',value=r'')

            # In bedrooms, convert "bachelor" to 0
            df['bedrooms'].replace(inplace=True,to_replace='bachelor',value=0)

            #Add the date the data was retrieved
            df['retrieval_date'] = pd.to_datetime('today').strftime("%m/%d/%Y")

            df.to_csv('test19.csv')


    try:
        # Connect to the database (exception raised if not connected)
        conn = db.connect()

        # Prepare a statement
        statement = db.sql_writer_insert('rental_data', list(df))

        for index,row in df.iterrows():

            rental = Rental.Rental(row["address"], row["address_hidden"],row["availability"],row["avdate"],row["baths"],
            row["bedrooms"],row["cats"],row["city"],row["community"],row["den"],row["dogs"], row["email"], row["id"], 
            row["intro"],row["latitude"],row["link"],row["location"], row["longitude"],row["marker"],row["phone"],row["phone_2"],
            row["preferred_contact"], row["price"], row["province"], row["quadrant"], row["ref_id"], row["rented"], row["slide"],
            row["sq_feet"], row["status"],row["thumb"],row["thumb2"], row["title"], row["type"], row["userId"],"NULL", row["website"], 
            row["retrieval_date"]) 

            # TODO: The utilities column has [] around its contents, mysql thinks its a list within a list...
            # TODO: Object validation

            db.insert(conn, rental, statement)  # exception NOT raised if data not inserted

        conn.close()

    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        logging.info(message)
        raise

    finally:
        logging.info("Au revoir")


if __name__ == "__main__":
    main()
    # TODO: Handle raised exceptions
    # TODO: Write tests