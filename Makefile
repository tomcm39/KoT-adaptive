#mcandrew;

PYTHON := python3 -W ignore
R := Rscript --vanilla
CDCEPIREPO := ../FluSight-forecasts/

runAll: updatedata\
	updateFluSight\
	moveFluSightForecasts2CurrentDir\
	scoreComponentModels\
	createListOfExcludedModelsFromEnsemble\
	assignWeights2ComponentModels\
	produceEnsembleForecast\
	produceCompleteEnsembleForecasts\
	validateEnsembleForecast\
	runChecks

updatedata:
	mkdir -p data && mkdir -p historicalData &&\
	$(PYTHON) downloadLatestData.py &&\
	echo "Latest Data Downloaded"

updateFluSight:
	git -C $(CDCEPIREPO) pull &&\
	echo "Updated FluSight Repository"

moveFluSightForecasts2CurrentDir:
	mkdir -p historicalForecasts && mkdir -p forecasts &&\
	$(PYTHON) moveFluSightForecasts2CurrentDir.py &&\
	echo "Historical Forecasts and Current Forecast updated"

scoreComponentModels:
	mkdir -p historicalScores && mkdir -p scores &&\
	$(PYTHON) scoreComponentModels.py &&\
	echo "Component models scored"

createListOfExcludedModelsFromEnsemble:
	mkdir -p historicalExcludedModels && mkdir -p excludedModels && \
	$(PYTHON) createSetOfExcludedModels.py && \
	echo "created set of excluded models"

assignWeights2ComponentModels:
	mkdir -p historicalWeights && mkdir -p weights &&\
	$(PYTHON) computeAdaptiveEnsembleWeights.py --prior 10 &&\
	echo "Adaptive ensemble weights assigned"

produceEnsembleForecast:
	mkdir -p historicalEnsembleForecasts && mkdir -p ensembleForecasts &&\
	$(PYTHON) produceEnsembleForecast.py &&\
	echo "Adaptive Ensemble Forecast produced"

produceCompleteEnsembleForecasts:
	mkdir -p historicalEnsembleForecastsForAllEW && mkdir -p ensembleForecastsForAllEW &&\
	$(PYTHON) produceEnsembleForecastForAllPastEpidemicWeeks.py &&\
	echo "Adaptive Ensemble Forecast produced for all past EWs"

validateEnsembleForecast:
	$(R) validateSubmission.R

runChecks:
	$(PYTHON) countNumberOfLogScoresPerModel.py && \
	$(PYTHON) countNumberOfModelsInFluSight.py && \
	$(PYTHON) countNumberOfModelsWithScores.py && \
	echo "Completed forecast checks"

createVis:
	mkdir -p historicalVis && mkdir -p vis \
	$(PYTHON) vis_ensemble_forecasts.py && \
	$(PYTHON) vis_weightsByModel.py && \
	$(PYTHON) vis_weights_plotted_against_avgLogScore.py
