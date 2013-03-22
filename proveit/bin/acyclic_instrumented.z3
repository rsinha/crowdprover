(declare-sort Node)
(declare-fun next (Node) Node)
(declare-fun data (Node) Int)
(declare-fun rnext (Node Node) Bool)
(declare-fun bnext (Node) Node)
(declare-fun iter () Node)

(declare-const head Node)
(declare-const null Node)

;Axiom AX1
(assert (forall ((u Node) (v Node))
          (and
            (=> (rnext u v) (or (= u v) (and (not (= (next u) null)) (rnext (next u) v))))
            (=> (or (= u v) (and (not (= (next u) null)) (rnext (next u) v))) (rnext u v))
          )
))
;Axiom AX2
(assert (forall ((u Node)) 
  (= (bnext u) (ite (= (next u) null) (next u) (bnext (next u))))
))
;Axiom Transitivity
(assert (forall ((u Node) (v Node) (w Node))
  (=> (and (rnext u v) (rnext v w)) (rnext u w))
))
;Axiom Antisymmetry
(assert (forall ((u Node) (v Node))
  (=> (and (rnext u v) (rnext v u)) (= u v))
))

;loopcond negated
(assert (= iter null))
;loopinv
(assert (forall ((v Node))
  (=> (rnext head v) (or (= (data v) 42) (and (not (= iter null)) (rnext iter v))))
))

;postcond negated
(assert (not (forall ((v Node))
  (=> (rnext head v) (= (data v) 42))
)))

(check-sat)
