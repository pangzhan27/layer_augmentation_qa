import sys
sys.path.insert(0, '../')

import torch
from torch import nn
from torch.autograd import Variable
from holder import *
from util import *
from constr_utils import *


# A content word in the hypothesis should align to a content word that is in relation set.
# Let R denotes conceptnet alignment
# Let A denotes unconstrained model belief on alignment
# Let A' denotes constrained/augmented model belief
# R_i and A_i -> A_i'

# NOTE, if a content hypo word has no such related content premise word, then skip
class A8(torch.nn.Module):
	def __init__(self, opt, shared):
		super(A8, self).__init__()
		self.opt = opt
		self.shared = shared

		self.one = Variable(torch.Tensor([1.0]), requires_grad=False)
		self.zero = Variable(torch.Tensor([0.0]), requires_grad=False)
		if opt.gpuid >= 0:
			self.one = self.one.cuda()
			self.zero = self.zero.cuda()


	# run logic of A8
	#	assumes the input att is of shape (batch_l, context_l, max_query_l)
	def logic(self, att):
		# first get the content relation selectors
		c_content_selector = get_c_selector(self.opt, self.shared, 'content_word').view(self.shared.batch_l, self.shared.context_l, 1)
		q_content_selector = get_q_selector(self.opt, self.shared, 'content_word').view(self.shared.batch_l, 1, self.shared.max_query_l)
		# content word alignment selector
		C = c_content_selector * q_content_selector
		# related alignment selector
		R = get_rel_selector1(self.opt, self.shared, 'all_rel')
		# select content alignment
		R = Variable(C * R, requires_grad=False)
		if self.opt.gpuid != -1:
			R = R.cuda()

		#d = att * R
		d = torch.max(self.zero, att + R - self.one)

		return d

	def forward(self, att):
		return self.logic(att)