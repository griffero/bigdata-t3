from mrjob.job import MRJob
from mrjob.step import MRStep
from mrjob.protocol import JSONValueProtocol
from mr3px.csvprotocol import CsvProtocol
import time
import csv

DATA_TYPE = 0
CATEGORIES = 1
REVIEW_ID = 1
STARS = 2

class CountBusinessStarsPerCategory(MRJob):
    INPUT_PROTOCOL = JSONValueProtocol

    def initial_map(self, _, line):
        data = line
        if data.get("user_id"):
            # business_id, ["review", review_id, stars]
            yield data["business_id"], ["review", data["review_id"], data["stars"]]
        elif data.get("business_id"):
            # business_id, ["business", categories]
            yield data["business_id"], ["business", data["categories"], data["address"], data["city"], data["state"], data["postal_code"], data["latitude"], data["longitude"]]

    def reducer_join(self, key, values):
        business_raw_information = list(values)
        business_reviews = []
        business_categories = ""
        address = ""
        city = ""
        state = ""
        postal_code = ""
        latitude = ""
        longitude = ""
        for business_information in business_raw_information:
            if business_information[DATA_TYPE] == "business":
                business_categories = business_information[CATEGORIES]
                address = business_information[2].encode('utf-8')
                city = business_information[3].encode('utf-8')
                state = business_information[4].encode('utf-8')
                postal_code = business_information[5].encode('utf-8')
                latitude = business_information[6]
                longitude = business_information[7]
            elif business_information[DATA_TYPE] == "review":
                business_reviews.append([business_information[REVIEW_ID], business_information[STARS]])
        for review in business_reviews:
            for category in business_categories:
                review_id = review[0]
                review_stars = review[1]
                output = [review_id, category, review_stars, address, city, state, postal_code, latitude, longitude]
                writer.writerow(output)
                yield ("", output)

    def steps(self):
        return [
            MRStep(
                mapper=self.initial_map,
                reducer=self.reducer_join
                )
            ]

if __name__ == '__main__':
    header = ["review_id", "category", "stars"]
    output_file  = open('complete.csv', "wb")
    writer = csv.writer(output_file)
    writer.writerow(header)
    CountBusinessStarsPerCategory.run()
    output_file.close()
