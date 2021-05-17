#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test attention
"""
import unittest
import torch
from torch import tensor
from torch import nn
import torch_sparse
from function_transformer_attention import SpGraphTransAttentionLayer, ODEFuncTransformerAtt
from torch_geometric.utils import softmax, to_dense_adj
from data import get_dataset
from GNN_KNN import GNN_KNN
from test_params import OPT
from graph_rewiring import apply_gdc
from graph_rewiring import apply_KNN, apply_beltrami

class KNNTests(unittest.TestCase):
  def setUp(self):
    self.edge = tensor([[0, 2, 2, 1], [1, 0, 1, 2]])
    self.x = tensor([[1., 2.], [3., 2.], [4., 5.]], dtype=torch.float)
    self.edge1 = tensor([[0, 0, 1, 1, 2, 2], [1, 2, 0, 2, 0, 1]])
    self.x1 = torch.ones((3, 2), dtype=torch.float)

    self.W = tensor([[2, 1], [3, 2]], dtype=torch.float)
    self.alpha = tensor([[1, 2, 3, 4]], dtype=torch.float)
    self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    opt = {'beltrami': True}
    self.opt = {**OPT, **opt}
    self.dataset = get_dataset(self.opt, '../data', False)

  def tearDown(self) -> None:
    pass


  def test_gnn(self):
    pos_encoding = apply_beltrami(self.dataset.data, self.opt)
    self.assertTrue(pos_encoding.shape == torch.Size([self.dataset.data.num_nodes, self.dataset.data.num_nodes]))
    self.opt['pos_enc_dim'] = pos_encoding.shape[1]
    gnn = GNN_KNN(self.opt, self.dataset, device=self.device)
    gnn.train()
    out = gnn(self.dataset.data.x, pos_encoding)
    self.assertTrue(out.shape == torch.Size([self.dataset.data.num_nodes, self.dataset.num_classes]))
    gnn.eval()
    out = gnn(self.dataset.data.x, pos_encoding)
    self.assertTrue(out.shape == torch.Size([self.dataset.data.num_nodes, self.dataset.num_classes]))

if __name__ == '__main__':
  BT = KNNTests()
  BT.setUp()
  BT.test_gnn()