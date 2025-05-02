module mul(
	input			clk,
	input		[31:0]	x,
	input		[31:0]	y,
	output	reg	[31:0]	p
);
	always @(posedge clk) begin
		p <= x * y;
	end
endmodule
