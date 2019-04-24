Brownout Replica Controller Simulator
=====================================

The aim of this simulator is allow quick testing of new brownout replica controller.
More information about brownout can be found in the following article:

> Cristian Klein, Martina Maggio, Karl-Erik Årzén, Francisco Hernández-Rodriguez,
> "Brownout: Building More Robust Cloud Applications", ICSE, 2014

A pre-print of the original paper can be downloaded [here](http://www8.cs.umu.se/~cklein/publications/icse2014-preprint.pdf).

This branch contains modifications and experiments for the following paper, to be published at ICAC 2019:

> Lars Larsson, William Tärneberg, Cristian Klein, Erik Elmroth
> Quality-Elasticity: Improved resource utilization, throughput, and response times via adjusting output quality to current operating conditions

Pre-print to be made available shortly, and BibTeX citation when published.

Abstract of ICAC 2019 paper
---------------------------

> This work addresses two related problems for on-line services, namely poor resource utilization during regular operating conditions, and low throughput, long response times, or poor performance under periods of high system load. To address these problems, we introduce our notion of quality-elasticity as a manner of dynamically adapting response qualities from software services along a fine-grained spectrum. When resources are abundant, response quality can be increased, and when resources are scarce, responses are delivered at a lower quality to prioritize throughput and response times. We present an example of how a complex online shopping site can be made quality-elastic. Experiments show that, compared to state of the art, improvements in throughput (57%  more served queries), lowered response times (8 time reduction for 95th percentile responses), and an estimated 40% profitability increase can be made using our quality-elastic approach. When resources are abundant, our approach may achieve upwards of twice as high resource utilization as prior work in this field.


Usage
-----

To conduct the experiments, we used Ubuntu 16.04 LTS. Other software has been installed from the official repositories, specifically:

* Python
* Numpy

Installing this software on top of Ubuntu can be achieved using the following commands:

    sudo apt-get install python python-numpy

Running sensitivity analysis to tune the Brownout controller can be done using the `parameters.sh` script by supplying it with an experiment name, e.g. `./parameters.sh brownout-tuning`.

Running experiments can be done using `experiments.sh` and an experiment name, e.g. `./experiments.sh testing`.

In either case, the output winds up in the `experiments/` directory.

For questions or comments, please contact Lars Larsson <lastname@cs.umu.se>.


