module hello(input clk);
	reg [31:0]	i = 0;
	initial begin
		$display("start");
		$dumpfile("dump.vcd");
		$dumpvars();
	end
	always @(posedge clk) begin
		if (i == 1000) begin
			$display("stop");
			$finish;
		end
		i <= i+1;
	end
endmodule
