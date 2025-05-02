module add(
	input			clk,
	input		[7:0]	x,
	input		[7:0]	y,
	output	reg	[7:0]	s
);
	always @(posedge clk) begin
		s <= x + y;
	end
endmodule
