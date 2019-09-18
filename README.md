# QThought - a platform to simulate thought experiments with quantum agents

We introduce a software package that allows users to design and run simulations of thought experiments in quantum theory. In particular, it covers cases where reasoning agents are modelled as quantum systems, such as Wigner's friend experiment. Users can customize the protocol of the experiment, the inner workings of agents (e.g.\ the quantum circuit that models their reasoning process), the abstract logical system used (which may or not allow agents to combine premises and make inferences about each other's reasoning), and the interpretation of quantum theory used by different agents (for example collapse, Copenhagen, many worlds or Bohmian mechanics). 
The software is written in a quantum programming language, [ProjectQ], and as such the simulations of thought experiments can in principle run on quantum hardware. 


## Getting started

Our software platform is based on [ProjectQ]. To install it, please follow the instructions in [Tutorials]. 
To access Jupyter notebooks, follow guidelines at the [Jupyter website].


## Documentation and examples

The project is structured as follows: users can customize the protocol of the experiment, the inner workings of agents (e.g. the quantum circuit that models their reasoning process), the abstract logical system used (which may or not allow agents to combine premises and make inferences about each other's reasoning), and the interpretation of quantum theory used by different agents (for example collapse, Copenhagen, many worlds or Bohmian mechanics). In the corresponding folders, we give examples of how one can program all of the mentioned above, and a PDF file with a technical explanation; the list of the examples is going to extend over time. Additionally, all protocols are accompannied by a Jupyter notebook, explaining every step in a simple fashion.

0. Schematic software structure and motivation: [qthought/software_structure][SoftStr]
1. Protocol examples: 
    - simple protocols [qthought/simple examples][SimplEx]
    - Frauchiger-Renner thought experiment [qthought/Frauchiger-Renner example][FREx]

2. Consistency rules, logical reasoning:
    - modal logic [qthought/logical reasoning][ModalC]

3. Interpretations:
    - Copenhagen interpretation [qthought/interpretations/copenhagen_theory][CopT]
    - collapse theories [qthought/interpretations/collapse_theory][ColT]

## Please cite

When using ProjectQ for research projects, please cite
  - [arxiv number to appear]

## Authors

The first release of QThought was developed by Simon Mathis, Nuriya Nurgalieva, Lídia del Rio and Renato Renner at ETH Zürich.

## License

QThought is licensed under the MIT License.



[ProjectQ]: <https://projectq.ch>
[Tutorials]: <https://projectq.readthedocs.io/en/latest/tutorials.html>
[Jupyter website]: <https://jupyter.readthedocs.io/en/latest/content-quickstart.html>
[SimplEx]: <https://github.com/Croydon-Brixton/qthought/blob/master/qthought/simple%20examples>
[FREx]: <https://github.com/Croydon-Brixton/qthought/tree/master/qthought/Frauchiger-Renner%20example>
[ModalC]: <https://github.com/Croydon-Brixton/qthought/blob/master/qthought/logical%20reasoning/consistency.py>
[CopT]: <https://github.com/Croydon-Brixton/qthought/blob/master/qthought/interpretations/copenhagen_theory.py>
[ColT]: <https://github.com/Croydon-Brixton/qthought/blob/master/qthought/interpretations/collapse_theory.py>
[SoftStr]: <https://github.com/Croydon-Brixton/qthought/blob/master/qthought/software_structure.pdf>
