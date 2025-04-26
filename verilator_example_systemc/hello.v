module hello(input clk);
	always @(posedge clk) begin
		$display("hello.");
		$finish;
	end
endmodule
