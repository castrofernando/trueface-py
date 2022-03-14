class Events:
    def __init__(self,file_name,name,event_date,execution_time):
         self.file_name = file_name
         self.name = name
         self.event_date = event_date
         self.execution_time = execution_time


    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)
