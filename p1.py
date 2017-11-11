from mrjob.job import MRJob
from mrjob.step import MRStep
from mrjob.protocol import JSONValueProtocol
from mr3px.csvprotocol import CsvProtocol
import time

DATA_TYPE = 0
CATEGORIES = 1
STARS = 1

class CountBusinessStarsPerCategory(MRJob):
    INPUT_PROTOCOL = JSONValueProtocol
    OUTPUT_PROTOCOL = CsvProtocol

    def map_business_id_with_review_or_categories(self, _, line):
        data = line
        if data.get("user_id"):
            # business_id, ["review", review_id, stars]
            yield data["business_id"], ["review", data["stars"]]
        elif data.get("business_id"):
            # business_id, ["business", categories]
            yield data["business_id"], ["business", data["categories"]]

    def reduce_business_information(self, key, values):
        business_raw_information = list(values)
        business_stars = []
        business_categories = ""
        for business_information in business_raw_information:
            if business_information[DATA_TYPE] == "business":
                business_categories = business_information[CATEGORIES]
            elif business_information[DATA_TYPE] == "review":
                business_stars.append(business_information[STARS])
        for star in business_stars:
            for category in business_categories:
                yield (category, star)

    def reduce_by_categories(self, key, values):
        yield "out", [key, list(values)]

    def steps(self):
        return [
            MRStep(
                mapper=self.map_business_id_with_review_or_categories,
                reducer=self.reduce_business_information
                ),
            MRStep(
                reducer=self.reduce_by_categories
                )
            ]

if __name__ == '__main__':
    CountBusinessStarsPerCategory.run()
