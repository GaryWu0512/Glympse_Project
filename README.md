# Glympse_Project

## Query

## Maneuver Detection

## Scoring
* all scoring functions are contained in scoring_func.py
* scoring requires a sample population of detected maneuvers - population_new.csv is the example sample population
* Sample population must contain at least 100 agents
* Agents in the sample population should have minimum driver time of 10 hours

#### get_scores_example(agent_id, sample_pop_file)
```scores an agent from the sample population against the sample population```

#### get_scores(maneuver_filename, sample_pop_file)
```scores an agent from a separate file (must be csv) against the sample population```
