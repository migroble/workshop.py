# Script by Peppermint#2241

rule "fibonacci":
	n = 20
	
	switch fib:
		case global_A == 0:
			set_at_index(global_B, 1, 0)
			set_at_index(global_B, 1, 1)
			set(global_A, 2)
		case:
			set_at_index(global_B, global_A, global_B[global_A - 1] + global_B[global_A - 2])
			modify(global_A, "add", 1)
	
	add_condition(global_A < n)
	add_action(fib, wait(0.016, abort_when_false), loop)