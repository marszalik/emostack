from emostack.action.actionFactory import actionFactory
from emostack.construct.constructFactory import constructFactory
from emostack.containers.AccessibilitySlot import AccessibilitySlot
from emostack.disposition.carriedLines import carriedLines
from emostack.emoThought.feelingWords import feelingWords
from emostack.episode.eventWords import eventWords
from emostack.hippocampus.Hippocampus import Hippocampus
from emostack.laws.fadingLaw import fadingLaw
from emostack.laws.forgettingThreshold import forgettingThreshold
from emostack.laws.reconsolidationLaw import reconsolidationLaw
from emostack.processes.appraisal.appraisal import appraisal
from emostack.processes.dispositionLearning.dispositionLearning import dispositionLearning
from emostack.processes.dispositionSelection.dispositionSelection import dispositionSelection
from emostack.processes.encoding.encoding import encoding
from emostack.processes.fading.fading import fading
from emostack.processes.introspection.constructFormation import constructFormation
from emostack.processes.introspection.introspection import introspection
from emostack.processes.recall.associationFilter import associationFilter
from emostack.processes.recall.recall import recall
from emostack.processes.recall.ruminationClusters import ruminationClusters
from emostack.processes.reconsolidation.reconsolidation import reconsolidation
from emostack.processes.responding.responding import responding
from emostack.processes.sleep.sleep import sleep
from emostack.processes.summarising.summarising import summarising
from emostack.runtime.reflection import reflection
from emostack.runtime.turn import turn
from emostack.senses.Senses import Senses


class assembly:
    """Puts together the containers and processes of one being over the shared machinery."""

    def __init__(self, being, repositories, processor, embedder, time, presence, presenceKey, parameters):
        self.being = being
        self.repositories = repositories
        self.processor = processor
        self.embedder = embedder
        self.time = time
        self.presence = presence
        self.presenceKey = presenceKey
        self.parameters = parameters
        self.words = feelingWords()
        self.actions = actionFactory()
        self.rumination = ruminationClusters()
        self.fadingLaw = fadingLaw(parameters["fadeFloor"], parameters["fadeTauDays"],
                                   parameters["fadeNegativeSlowdown"])
        self.hippocampus = Hippocampus(being.id, repositories["hippocampus"])
        self.slot = AccessibilitySlot(being.id, self.hippocampus, repositories["slot"], parameters["slotSize"],
                                      parameters["slotDays"])
        self.fading = fading(self.hippocampus, self.fadingLaw, time)
        self.reconsolidation = reconsolidation(self.hippocampus, self.fading,
                                               reconsolidationLaw(parameters["strengthClosing"]), time)

    def recall(self):
        return recall(self.hippocampus, self.embedder,
                      associationFilter(self.processor, self.words, self.parameters["filterKeep"]),
                      self.rumination, self.fadingLaw, self.time, self.parameters["recallCandidates"],
                      self.parameters["nameBonus"], self.parameters["strengthPassesFilter"])

    def reflection(self):
        return reflection(self.being, self.hippocampus, self.slot, introspection(self.processor, self.actions),
                          constructFormation(self.hippocampus, self.embedder, constructFactory(), self.time,
                                             self.parameters["constructDuplicate"],
                                             self.parameters["constructReinforcement"]),
                          self.reconsolidation, self.recall(), self.time, self.words,
                          self.parameters["introspectionEntries"], self.parameters["reflectionMaxSteps"],
                          self.parameters["episodesPerFeeling"])

    def sleep(self):
        return sleep(self.processor, self.hippocampus, self.time, self.words,
                     forgettingThreshold(self.parameters["forgettingCurve"]), self.parameters["anchorMinimum"])

    def turnFor(self, conversation):
        dispositions = self.repositories["dispositions"]
        return turn(
            conversation, self.hippocampus, self.slot, self.recall(), responding(self.processor, self.actions),
            appraisal(self.processor), encoding(self.hippocampus, self.embedder),
            self.reconsolidation, summarising(self.processor, self.parameters["summaryThreadCap"]),
            dispositionSelection(self.processor, dispositions, self.parameters["dispositionsBase"],
                                 self.parameters["dispositionsMax"]),
            dispositionLearning(self.processor, dispositions, self.time, self.parameters["dispositionsBase"]),
            self.reflection(), self.presence, self.presenceKey, carriedLines(self.hippocampus), eventWords(),
            Senses.words(),
            self.time, self.words, self.fadingLaw, self.rumination, self.parameters)
