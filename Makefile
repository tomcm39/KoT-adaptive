#mcandrew;

PYTHON := python3 -W ignore
R := Rscript --vanilla

runAll: updatedata\
	updateFluSight\
	moveFluSightForecasts2CurrentDir\
	scoreComponentModels\
	assignWeights2ComponentModels\
	produceEnsembleForecast\
	validateEnsembleForecast

updatedata:
	mkdir -p data && mkdir -p historicalData &&\
	$(PYTHON) downloadLatestData.py &&\
	echo "Latest Data Downloaded"

updateFluSight:
	git -C ../FluSight-forecasts/ pull &&\
	echo "Updated FluSight Repository"

moveFluSightForecasts2CurrentDir:
	mkdir -p historicalForecasts && mkdir -p forecasts &&\
	$(PYTHON) moveFluSightForecasts2CurrentDir.py &&\
	echo "Historical Forecasts and Current Forecast updated"

scoreComponentModels:
	mkdir -p historicalScores && mkdir -p scores &&\
	$(PYTHON) scoreComponentModels.py &&\
	echo "Component models scored"

assignWeights2ComponentModels:
	mkdir -p historicalWeights && mkdir -p weights &&\
	$(PYTHON) computeAdaptiveEnsembleWeights.py --prior 10 &&\
	echo "Adaptive ensemble weights assigned"

produceEnsembleForecast:
	mkdir -p historicalEnsembleForecasts && mkdir -p ensembleForecasts &&\
	$(PYTHON) produceEnsembleForecast.py &&\
	echo "Adaptive Ensemble Forecast produced"

validateEnsembleForecast:
	$(R) validateSubmission.R
