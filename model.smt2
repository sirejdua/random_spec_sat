; benchmark generated from python API
(set-info :status unknown)
(declare-fun |a_{1x}| () (_ BitVec 3))
(declare-fun |a_{0x}| () (_ BitVec 3))
(declare-fun |a_{1y}| () (_ BitVec 3))
(declare-fun |a_{0y}| () (_ BitVec 3))
(declare-fun |s_{2x}| () (_ BitVec 3))
(declare-fun |s_{1x}| () (_ BitVec 3))
(declare-fun |s_{0x}| () (_ BitVec 3))
(declare-fun |s_{2y}| () (_ BitVec 3))
(declare-fun |s_{1y}| () (_ BitVec 3))
(declare-fun |s_{0y}| () (_ BitVec 3))
(assert
 (and (bvsle |a_{0x}| (_ bv1 3)) (bvsle |a_{1x}| (_ bv1 3))))
(assert
 (and (bvsge |a_{0x}| (_ bv7 3)) (bvsge |a_{1x}| (_ bv7 3))))
(assert
 (and (bvsle |a_{0y}| (_ bv1 3)) (bvsle |a_{1y}| (_ bv1 3))))
(assert
 (and (bvsge |a_{0y}| (_ bv7 3)) (bvsge |a_{1y}| (_ bv7 3))))
(assert
 (and (bvsle |s_{0x}| (_ bv1 3)) (bvsle |s_{1x}| (_ bv1 3)) (bvsle |s_{2x}| (_ bv1 3))))
(assert
 (and (bvsge |s_{0x}| (_ bv6 3)) (bvsge |s_{1x}| (_ bv6 3)) (bvsge |s_{2x}| (_ bv6 3))))
(assert
 (and (bvsle |s_{0y}| (_ bv1 3)) (bvsle |s_{1y}| (_ bv1 3)) (bvsle |s_{2y}| (_ bv1 3))))
(assert
 (and (bvsge |s_{0y}| (_ bv6 3)) (bvsge |s_{1y}| (_ bv6 3)) (bvsge |s_{2y}| (_ bv6 3))))
(assert
 (and (= |s_{1x}| (bvadd |s_{0x}| |a_{0x}|)) (= |s_{2x}| (bvadd |s_{1x}| |a_{1x}|))))
(assert
 (and (= |s_{1y}| (bvadd |s_{0y}| |a_{0y}|)) (= |s_{2y}| (bvadd |s_{1y}| |a_{1y}|))))
(assert
 (and (= |s_{0x}| (_ bv0 3))))
(assert
 (and (= |s_{0y}| (_ bv0 3))))
(export-to-dimacs "model.cnf")
(check-sat)
