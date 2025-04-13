module top(
	input	clk,
	input	ftdi_rx,
	output	D1,
	output	D2,
	output	D3,
	output	D4,
	output	D5,
	output	ftdi_tx,
	output	p44,
	output	p45,
	output  pdm_clk,
	input   pdm_dat
);
	wire clk_uart;

	reg [7:0]	char = 8'h6f;
	reg		go = 0;
	wire		uart_ready;

	rot		rot_1(ftdi_rx, {D1, D2, D3, D4});

	//assign p44 = go;
	//assign p45 = ftdi_tx;

	assign p44 = pdm_clk;
	assign p45 = pdm_dat;

	clk_div_uart	clk_div_uart_1(clk, clk_uart);
	uart_tx		uart_tx_1(clk_uart, char, go, ftdi_tx, uart_ready);

	reg [15:0] t = 0;
	always @(posedge clk_uart) begin
		if (t<128) begin
			if (!go && uart_ready) begin
				char <= pdm[t[6:0]] ? 8'h31 : 8'h30;
				go <= 1;
				t <= t+1;
			end
			if (go && !uart_ready) begin
				go <= 0;
			end
		end else begin
			if (!ftdi_rx) begin
				t <= 0;
			end
		end
	end

	reg led5 = 0;
	assign D5 = led5;

	clk_div_pdm	clk_div_pdm_1(clk, pdm_clk);

	reg [15:0]	pdm_t = 0;
	reg		pdm	[127:0];
	always @(posedge pdm_clk) begin
		if (pdm_t < 128) begin
			pdm[pdm_t[6:0]] <= pdm_dat;
			pdm_t <= pdm_t+1;
		end else if (pdm_t == 128) begin
			led5 <= 1;
		end
	end
endmodule

module clk_div_pdm(input clk, output reg clk_pdm);
	reg [3:0] t = 0;
	always @(posedge clk) begin
		t <= t<12-1 ? t+1 : 0;
		clk_pdm <= t<6;
	end
endmodule

module rot(input clk, output [3:0] d);
	reg [3:0]	r = 4'b1000;
	always @(posedge clk) r <= {r[0], r[3:1]};
	assign d = r;
endmodule

module clk_div_uart(input clk, output reg clk_uart);
	reg [10:0] t = 0;
	always @(posedge clk) begin
		t <= t<1250-1 ? t+1 : 0;
		clk_uart <= t<625;
	end
endmodule

module uart_tx(input clk, input [7:0] char, input go, output reg tx, output reg ready);
	parameter s_ready =  0;
	parameter s_start =  1;
	parameter s_data0 =  2;
	parameter s_data1 =  3;
	parameter s_data2 =  4;
	parameter s_data3 =  5;
	parameter s_data4 =  6;
	parameter s_data5 =  7;
	parameter s_data6 =  8;
	parameter s_data7 =  9;
	parameter s_stop1 = 10;
	parameter s_stop2 = 11;
	parameter s_stop3 = 12;
	parameter s_stop4 = 13;

	reg [3:0]	state = s_ready;
	reg [7:0]	data = 8'h41;

	always @(posedge clk) begin
		ready <= state == s_ready;
		case (state)
			s_ready: begin
				if (go) begin
					data <= char;
					state <= s_start;
				end
			end
			s_start:	state <= s_data0;
			s_data0:	state <= s_data1;
			s_data1:	state <= s_data2;
			s_data2:	state <= s_data3;
			s_data3:	state <= s_data4;
			s_data4:	state <= s_data5;
			s_data5:	state <= s_data6;
			s_data6:	state <= s_data7;
			s_data7:	state <= s_stop1;
			s_stop1:	state <= s_stop2;
			s_stop2:	state <= s_stop3;
			s_stop3:	state <= s_stop4;
			s_stop4: begin
				if (!go)
					state <= s_ready;
			end
		endcase
		case (state)
			s_ready:	tx <= 1;
			s_start:	tx <= 0;
			s_data0:	tx <= data[0];
			s_data1:	tx <= data[1];
			s_data2:	tx <= data[2];
			s_data3:	tx <= data[3];
			s_data4:	tx <= data[4];
			s_data5:	tx <= data[5];
			s_data6:	tx <= data[6];
			s_data7:	tx <= data[7];
			s_stop1:	tx <= 1;
			s_stop2:	tx <= 1;
			s_stop3:	tx <= 1;
			s_stop4:	tx <= 1;
		endcase
	end
endmodule
