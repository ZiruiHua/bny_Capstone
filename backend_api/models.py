from django.db import models


class Attribute(models.Model):
    name = models.TextField(default="")

class System(models.Model):
    name = models.TextField(default="")
    color = models.TextField(default="#3c763d")
    attributes = models.ManyToManyField(Attribute)
    #connectionsTo = models.ManyToManyField('self', symmetrical = False)
    #connectionsFrom = models.ManyToManyField('self', symmetrical = False)

    def addConnectionTo(self, otherSystem):
        self.connectionsTo.add(otherSystem)

    def addConnectionFrom(self, otherSystem):
        self.connectionsFrom.add(otherSystem)

    def __str__ (self):
        return self.name

class Relationship(models.Model):
    fromSystem = models.ForeignKey(System, related_name="relationsTo", on_delete=models.CASCADE)
    toSystem =  models.ForeignKey(System, related_name="relationsFrom", on_delete=models.CASCADE)
    attributes = models.ManyToManyField(Attribute, related_name="rel_attributes")