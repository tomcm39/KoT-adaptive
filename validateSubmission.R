#mcandrew;
require(FluSight)
fileName = list.files('./ensembleForecasts/')[1]
file = sprintf('./ensembleForecasts/%s',fileName)

if (verify_entry_file(file)){
    cat('Submisson file valid\n')
}else {cat('Error in submission file\n')}
