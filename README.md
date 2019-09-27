# QThought - a platform to simulate thought experiments with quantum agents

We introduce a software package that allows users to design and run simulations of thought experiments in quantum theory. In particular, it covers cases where reasoning agents are modelled as quantum systems, such as Wigner's friend experiment. Users can customize the protocol of the experiment, the inner workings of agents (e.g.\ the quantum circuit that models their reasoning process), the abstract logical system used (which may or not allow agents to combine premises and make inferences about each other's reasoning), and the interpretation of quantum theory used by different agents (for example collapse, Copenhagen, many worlds or Bohmian mechanics). 
The software is written in a quantum programming language, [ProjectQ], and as such the simulations of thought experiments can in principle run on quantum hardware. 


## Getting started

Our software platform is based on [ProjectQ]. To install it, please follow the instructions in [Tutorials]. 
To access Jupyter notebooks, follow guidelines at the [Jupyter website].

To install the pre-alpha version, you can use
```
pip install -i https://test.pypi.org/simple/ qthought
```

Alternatively, you can clone this github repository to your local machine, navigate to within the qthought folder and call
```
pip install .
``` 


## Documentation and examples

The project is structured as follows: users can customize the protocol of the experiment, the inner workings of agents (e.g. the quantum circuit that models their reasoning process), the abstract logical system used (which may or not allow agents to combine premises and make inferences about each other's reasoning), and the interpretation of quantum theory used by different agents (for example collapse, Copenhagen, many worlds or Bohmian mechanics). In the corresponding folders, we give examples of how one can program all of the mentioned above, and a PDF file with a technical explanation; the list of the examples is going to extend over time. Additionally, all protocols are accompannied by a Jupyter notebook, explaining every step in a simple fashion.

0. Schematic software structure and motivation: [qthought/software_structure][SoftStr]
1. Protocol examples: 
    - simple protocols [qthought/simpleExamples][SimplEx]
    - Frauchiger-Renner thought experiment [qthought/FrauchigerRennerExample][FREx]

2. Consistency rules, logical reasoning:
    - modal logic [qthought/logicalReasoning][ModalC]

3. Interpretations:
    - Copenhagen interpretation [qthought/interpretations/copenhagen_theory][CopT]
    - collapse theories [qthought/interpretations/collapse_theory][ColT]

## Basic elements to run

To run the protocol, one needs to:
    - specify the interpretation, namely *observe*, *forward_inference* and *backward_inference* in your interpretation description file;
    - specify the logic employed by agents, namely the method their predictions are glued together in *consistency*;
    - describe the protocol by summing it out of elements (some of them call *observe*, *forward_inference*,*backward_inference* and *consistency*) of *ProtocolStep* class.

If your protocol is correct and meets the requirements elaborated on in *Requirements* class, it yeilds the prediction after a run. 

For detailed instructions for how to assemble the protocol, please refer to the explanation provided in the Jupyter notebook [simple example I][Simple1].

## Current state of development

We have currently implemented two interpretations, namely, Copenhagen and collapse, and one model of logical reasoning (classical modal logic). Additionally, we have three example protocols that one can run on their own. 

In the future releases, we plan to extend this list by adding Bohmian mechanics and many-worlds interpretations, and weakening the logical reasoning structure.

## Please cite

When using QThought for research projects, please cite
  - [arxiv number to appear] 
  
As we are still in the process of preparing the arXiv submission, we kindly ask you to cite this repository instead.

## Authors

The first release of QThought was developed by Simon Mathis, Nuriya Nurgalieva, Lídia del Rio and Renato Renner at ETH Zürich.

## License

QThought is licensed under the [MIT License][MIT].



[ProjectQ]: <https://projectq.ch>
[Tutorials]: <https://projectq.readthedocs.io/en/latest/tutorials.html>
[Jupyter website]: <https://jupyter.readthedocs.io/en/latest/content-quickstart.html>
[SimplEx]: <https://github.com/Croydon-Brixton/qthought/blob/master/qthought/simpleExamples>
[FREx]: <https://github.com/Croydon-Brixton/qthought/tree/master/qthought/FrauchigerRennerExample>
[ModalC]: <https://github.com/Croydon-Brixton/qthought/blob/master/qthought/logicalReasoning/consistency.py>
[CopT]: <https://github.com/Croydon-Brixton/qthought/blob/master/qthought/interpretations/copenhagen_theory.py>
[ColT]: <https://github.com/Croydon-Brixton/qthought/blob/master/qthought/interpretations/collapse_theory.py>
[SoftStr]: <https://github.com/Croydon-Brixton/qthought/blob/master/qthought/software_structure.pdf>
[Simple1]: <https://github.com/Croydon-Brixton/qthought/blob/master/qthought/simpleExamples/simple%20example%20I.ipynb>
[MIT]: <https://www.opensource.org/licenses/MIT>
