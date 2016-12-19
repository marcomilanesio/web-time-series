class PersonPage:
    def __init__(self, person):
        self.name = person
        self.df = None
        self.important_dates = []
        self.birth_date = None
        self.death_date = None
        self.unique_contributors = None

    def add_birth_date(self, date):
        self.birth_date = date

    def add_death_date(self, date):
        self.death_date = date

    def add_important_date(self, date):
        self.important_dates.append(date)

    def add_unique_contributors(self, num):
        self.unique_contributors = num

    def add_dataframe(self, df):
        self.df = df

    def __str__(self):
        s = self.name
        s += "\nlen ts: {}".format(len(self.df))
        return s
