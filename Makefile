#mcandrew;

PYTHON := python3

runAll: updatedata updateFluSight moveFluSightForecasts2CurrentDir scoreComponentModels

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
	$(PYTHON) scoreComponentModels.py
