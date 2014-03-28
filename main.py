'''
This module is intended to duplicate the 'main()' function found in other
languages such as C++ and Java.  In order to run an experiment, this module
should be passed to your interpreter.  In the interest of speed and consistency
we suggest that PyPy 1.9.0 be used to run this code, although
Python 2.7 should be able to handle it correctly.

To see a full description of this modules command line arguments, run
````pypy main.py -h````.

Provided with this code should be the ``cfg`` folder which contains some
configuration files useful for running experiments.  These files can be passed
to main along with other configuration information in order to recreate
the experiments performed in the paper ``Analysis of Cartesian Genetic Programming's
Evolutionary Mechanisms``.  For example, the following command performs
one run of the Parity problem using seed number 13 with a genome size of
2000.  Also, verbose output is printed to the display,
the ``reorder`` variant is used, and the results are output to output/test_run.dat.

``pypy main.py cfg/once.cfg cfg/parity.cfg -seed 13 -g 200 -v -ordering reorder
-out test_run.dat``

For any support questions email brianwgoldman@acm.org.
'''

from evolution import Individual, multi_indepenedent
import problems
import util
from collections import defaultdict


def one_run(evaluator, config, frequencies):
    '''
    Performs a single run of the given configuration.  Returns a dictionary
    containing results.

    Parameters:

    - ``evaluator``: An object with the function get_fitness that takes an
      individual and returns its fitness value
    - ``config``: A dictionary containing all of the configuration information
      required to perform a experimental run, including:

      - All information required to initialize an individual.
      - All information required to run ``evolution.multi_independent``.
      - ``verbose``: Boolean value for if extra runtime information should
        be displayed.
      - ``max_evals``: The maximum number of evaluations allowed before
        termination.
      - ``max_fitness``: The fitness required to cause a "successful"
        termination.
    - ``frequencies``:  Dictionary used to return information about how often
      individuals of different lengths are evolved.  Set by evolution.generate.
    '''
    best = None
    last_improved = -1
    output = {'bests': []}
    generator = enumerate(multi_indepenedent(config, output, frequencies))
    for evals, individual in generator:
        individual.fitness = evaluator.get_fitness(individual)
        if best < individual:
            best = individual
            last_improved = evals
            if config['record_bests']:
                save = best.dump()
                save['evals'] = evals
                output['bests'].append(save)
                output['test_inputs'] = sorted(best.input_order.keys(),
                                               key=best.input_order.__getitem__)
            if config['verbose']:
                print '\t', last_improved, best.fitness, len(best.active)
        if (evals >= config['max_evals'] or
            best.fitness >= config['max_fitness']):
            break
    if config['verbose']:
        print "Best Found"
        print 'Before simplify', best.fitness, len(best.active)
        best.show_active()
        simplified = best.new(Individual.simplify)
        simplified.fitness = evaluator.get_fitness(simplified)
        print "After simplify", simplified.fitness, len(simplified.active)
        simplified.show_active()
    output.update({'fitness': best.fitness, 'evals': evals,
                   'success': best.fitness >= config['max_fitness'],
                   'phenotype': len(best.active),
                   'normal': output['skipped'] + evals,
                   'unused': sum(best.never_active)})
    return output


def all_runs(config):
    '''
    Perform all of the requested runs on a given problem.  Returns a two part
    tuple:

    - list of the dictionaries returned by ``one_run``.
    - frequency information collected by ``one_run``.

    Will give results for all
    completed runs if a keyboard interrupt is received.

    Parameters:

    - ``config``: Dictionary containing all configuration information required
      to perform all of the necessary runs of the experiment.  Should contain
      values for:

      - All configuration information needed by ``one_run``
      - ``problem``: The name of which problem from the ``problem`` module to
        run experiments on.
      - ``runs``: How many runs to perform
    '''
    # Construct the problem object
    evaluator = problems.__dict__[config['problem']](config)
    # Set configuration information from the problem
    config['function_list'] = evaluator.operators
    config['max_arity'] = evaluator.max_arity
    results = []
    frequencies = defaultdict(int)
    try:
        for run in range(config['runs']):
            print "Starting Run", run + 1
            result = one_run(evaluator, config, frequencies)
            print [(key, result[key]) for key in ['evals', 'fitness']]
            results.append(result)
    except KeyboardInterrupt:
        print "Interrupted"
    return results, frequencies


def combine_results(results):
    '''
    Given a list of result dictionaries, return analysis information such as
    the median values of each statistic as well as the median absolute
    deviation.

    Parameters:

    - ``results``: A list of dictionaries containing similar key values.
    '''
    combined = {}
    # Collect the successful runs
    successful = [result for result in results if result['success']]
    # Combine like keys across all runs
    for result in results:
        for key, value in result.iteritems():
            try:
                combined[key].append(value)
            except KeyError:
                combined[key] = [value]
    # Analyze the values for each key
    for key, value in combined.items():
        try:
            combined[key] = util.median_deviation(value)
        except TypeError:
            del combined[key]
    try:
        combined['success'] = len(successful) / float(len(results)), 0
    except ZeroDivisionError:
        combined['success'] = 0, 0
    return combined


def frequencies_to_vector(config, frequencies):
    '''
    Returns a flattened version of the frequencies dictionary.
    '''
    return [frequencies[index] for index in range(config['graph_length'])]

if __name__ == '__main__':
    import argparse
    import random
    import sys

    # Set up argument parsing
    description = 'Cartesian Genetic Programming.  In Python!'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('configs', metavar='Configuration Files',
                        type=str, nargs='+',
                        help='Zero or more json formatted files containing' +
                            ' configuration information')

    parser.add_argument('-g', dest='graph_length', type=int,
                        help='The number of nodes in the CGP graph')
    parser.add_argument('-m', dest='mutation_rate', type=float,
                        help='Use the specified mutation rate.')
    parser.add_argument('-i', dest='input_length', type=int,
                        help='The number of input nodes in the CGP graph')
    parser.add_argument('-o', dest='output_length', type=int,
                        help='The number of output nodes in the CGP graph')
    parser.add_argument('-pop_size', dest='pop_size', type=int,
                        help='Use the specified population size.')
    parser.add_argument('-seed', dest='seed', type=int,
                        help='Use the specified random seed used')
    parser.add_argument('-duplicate', dest='duplicate', type=str,
                        help='Specifies if evolution should should avoid' +
                        ' duplicated evaluations.  Valid settings are: ' +
                        'normal, skip, accumulate, single')
    parser.add_argument('-ordering', dest='ordering', type=str,
                        help='Specifies how to handle node ordering.' +
                        '  Valid settings are: ' +
                        'normal, reorder, dag')
    parser.add_argument('-record_bests', dest='record_bests',
                        action='store_true',
                        help='Include this flag to record the full genome' +
                        ' of the first individual to reach each new fitness.')
    parser.add_argument('-c', dest='output_config', type=str,
                        help='Outputs a single configuration file containing' +
                        ' the entire configuration used in this run')
    parser.add_argument('-v', dest='verbose', action='store_true',
                        help='Include this flag to increase periodic output')

    parser.add_argument('-out', dest='output_results', type=str,
                        help='Specify a file to output the results.')
    parser.add_argument('-freq', dest='frequency_results', type=str,
                        help='Specify a file to output the frequency results.')

    parser.add_argument('-profile', dest='profile', action='store_true',
                        help='Include this flag to run a profiler')

    # Perform argument parsing
    args = parser.parse_args()
    config = util.load_configurations(args.configs)
    config['verbose'] = args.verbose
    config['record_bests'] = args.record_bests

    if args.seed != None:
        config['seed'] = args.seed
    elif 'seed' not in config:
        config['seed'] = random.randint(0, sys.maxint)
    random.seed(config['seed'])

    # Allow the command line to override configuration file specifications
    if args.graph_length != None:
        config['graph_length'] = args.graph_length

    if args.mutation_rate != None:
        config['mutation_rate'] = args.mutation_rate

    if args.input_length != None:
        config['input_length'] = args.input_length

    if args.output_length != None:
        config['output_length'] = args.output_length

    if args.pop_size != None:
        config['pop_size'] = args.pop_size

    if args.duplicate != None:
        config['duplicate'] = args.duplicate

    if args.ordering != None:
        config['ordering'] = args.ordering

    if args.frequency_results != None:
        config['frequency_results'] = args.frequency_results

    if args.profile:
        # When profiling, just run the configuration
        import cProfile
        cProfile.run("all_runs(config)", sort=2)
        sys.exit()

    try:
        # Perform the actual run of the experiment
        raw_results, frequencies = all_runs(config)
        combined = sorted(combine_results(raw_results).items())
        print combined
        if args.output_results != None:
            # Output the results, with the combined stuff on the first line
            util.save_list(args.output_results, [combined] + raw_results)
        if args.output_config != None:
            # Serialize function list
            config['function_list'] = [func.__name__ for func in
                                       config['function_list']]
            # Saves the final configuration as a single file
            util.save_configuration(args.output_config, config)
        if args.frequency_results != None:
            # Saves the frequency information
            processed = frequencies_to_vector(config, frequencies)
            util.save_configuration(args.frequency_results, processed)
    except KeyError as e:
        print 'You must include a configuration value for', e.args[0]
