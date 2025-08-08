

module cic3_pdm (
    input  wire        clk,        // PDM clock
    input  wire        rst,        // active-high synchronous reset
    input  wire        pdm_in,     // 1-bit PDM data input
    input  wire [7:0]  hpf_alpha,  // HPF coefficient (0-255, 255=bypass)
    output wire signed [15:0] pcm_out, // Decimated PCM output
    output wire        pcm_valid

);
    //parameter DECIMATION = 64; // Decimation factor
    parameter OUTPUT_SHIFT = 10; // Can tune this

    // Internal registers
    reg signed [38:0] integrator_0 = 0;
    reg signed [38:0] integrator_1 = 0;
    reg signed [38:0] integrator_2 = 0;

    reg [5:0] decim_counter = 0;
    reg signed [38:0] comb_0 = 0, comb_1 = 0;

    /* verilator lint_off UNUSEDSIGNAL */
    reg signed [38:0] comb_2 = 0;

    // HPF registers
    reg signed [15:0] hpf_prev = 0;     // Previous input sample
    reg signed [15:0] cic_reg = 0;      // Registered CIC output
    reg cic_valid = 0;

    // CIC output
    wire signed [15:0] cic_out = comb_2[OUTPUT_SHIFT + 15 : OUTPUT_SHIFT];

    reg signed [38:0] delay_0 = 0, delay_1 = 0, delay_2 = 0;

    reg signed [15:0] pcm_out_r = 0;
    reg pcm_valid_r = 0;

    // Integrator stage (runs every clk)
    always @(posedge clk) begin
        if (rst) begin
            integrator_0 <= 0;
            integrator_1 <= 0;
            integrator_2 <= 0;
        end else begin
            integrator_0 <= integrator_0 + (pdm_in ? 1 : -1);
            integrator_1 <= integrator_1 + integrator_0;
            integrator_2 <= integrator_2 + integrator_1;
        end
    end

    // Decimation counter
    always @(posedge clk) begin
        if (rst)
            decim_counter <= 0;
        else
            decim_counter <= decim_counter + 1;
    end

    // Comb stage
    always @(posedge clk) begin
        cic_valid <= 0;
        if (rst) begin
            cic_reg <= 0;
        end else if (decim_counter == 63) begin
            comb_0 <= integrator_2 - delay_0;
            delay_0 <= integrator_2;
            comb_1 <= comb_0 - delay_1;
            delay_1 <= comb_0;
            comb_2 <= comb_1 - delay_2;
            delay_2 <= comb_1;
        end else if (decim_counter == 0) begin
            // CIC output is now stable, register it
            cic_reg <= cic_out;
            cic_valid <= 1;
        end
    end
    
    // HPF stage (runs after CIC settles)
    always @(posedge clk) begin
        pcm_valid_r <= 0;
        if (rst) begin
            hpf_prev <= 0;
            pcm_out_r <= 0;
        end else if (cic_valid) begin
            if (hpf_alpha == 8'd255) begin
                pcm_out_r <= cic_reg;
            end else begin
                // HPF: y[n] = x[n] - x[n-1] + alpha*y[n-1]
                pcm_out_r <= cic_reg - hpf_prev + ((pcm_out_r * hpf_alpha) >>> 8);
            end
            hpf_prev <= cic_reg;
            pcm_valid_r <= 1;
        end
    end

    assign pcm_out = pcm_out_r;
    assign pcm_valid = pcm_valid_r;

endmodule
