module cic3_pdm (
    input  wire        clk,           // PDM clock
    input  wire        rst,           // active-high synchronous reset
    input  wire        pdm_in,        // 1-bit PDM data input
    input  wire [7:0]  hpf_alpha,     // HPF coefficient (0-255, 255=bypass)
    input  wire [2:0]  scale_shift,   // Right shift amount (0-7 bits)
    output reg  signed [15:0] pcm_out, // Decimated PCM output
    output reg         pcm_valid       // Output valid pulse
);

    // CIC filter parameters
    localparam DECIMATION = 64;
    localparam CIC_WIDTH = 17;  // 17 bits for safe margin against overflow
    
    // CIC integrator and comb stages
    reg signed [CIC_WIDTH-1:0] integrator1, integrator2;
    reg signed [CIC_WIDTH-1:0] comb1, comb2;
    reg signed [CIC_WIDTH-1:0] comb1_d1, comb2_d1;
    
    // Decimation counter
    reg [6:0] decim_count;  // 7 bits to match DECIMATION width
    
    // CIC output and scaling
    reg signed [CIC_WIDTH-1:0] cic_out;
    reg signed [15:0] scaled_out;
    reg cic_valid;
    
    // HPF registers
    reg signed [15:0] hpf_x_prev;
    reg signed [15:0] hpf_y_prev;
    
    // HPF calculation wires
    /* verilator lint_off UNUSEDSIGNAL */
    wire signed [23:0] hpf_temp;
    /* verilator lint_on UNUSEDSIGNAL */
    wire signed [15:0] hpf_calc;
    
    // Convert 1-bit PDM to signed
    wire signed [CIC_WIDTH-1:0] pdm_signed = pdm_in ? 17'sd1 : -17'sd1;
    
    // CIC Integrator stages (run at PDM rate)
    always @(posedge clk) begin
        if (rst) begin
            integrator1 <= 0;
            integrator2 <= 0;
        end else begin
            integrator1 <= integrator1 + pdm_signed;
            integrator2 <= integrator2 + integrator1;
        end
    end
    
    // Decimation counter and CIC comb stages
    always @(posedge clk) begin
        if (rst) begin
            decim_count <= 0;
            comb1 <= 0;
            comb2 <= 0;
            comb1_d1 <= 0;
            comb2_d1 <= 0;
            cic_out <= 0;
            cic_valid <= 0;
        end else begin
            cic_valid <= 0;
            
            if (decim_count == DECIMATION - 1) begin
                decim_count <= 0;
                
                // Comb stage 1
                comb1 <= integrator2 - comb1_d1;
                comb1_d1 <= integrator2;
                
                // Comb stage 2
                comb2 <= comb1 - comb2_d1;
                comb2_d1 <= comb1;
                
                cic_out <= comb2;
                cic_valid <= 1;
            end else begin
                decim_count <= decim_count + 1;
            end
        end
    end
    
    // Output scaling
    always @(*) begin
        case (scale_shift)
            3'd0: scaled_out = cic_out[15:0];
            3'd1: scaled_out = cic_out[16:1];
            3'd2: scaled_out = {{1{cic_out[16]}}, cic_out[16:2]};  // Sign extend from bit 16
            3'd3: scaled_out = {{2{cic_out[16]}}, cic_out[16:3]};  // Sign extend from bit 16  
            3'd4: scaled_out = {{3{cic_out[16]}}, cic_out[16:4]};  // Sign extend from bit 16
            3'd5: scaled_out = {{4{cic_out[16]}}, cic_out[16:5]};  // Sign extend from bit 16
            3'd6: scaled_out = {{5{cic_out[16]}}, cic_out[16:6]};  // Sign extend from bit 16
            3'd7: scaled_out = {{6{cic_out[16]}}, cic_out[16:7]};  // Sign extend from bit 16
        endcase
    end
    
    // HPF calculation
    assign hpf_temp = ((hpf_alpha * hpf_y_prev) + (({8'd0, scaled_out} - {8'd0, hpf_x_prev}) << 8)) >>> 8;
    assign hpf_calc = hpf_temp[15:0];
    
    // High-pass filter (1st order IIR: y[n] = alpha/256 * y[n-1] + (x[n] - x[n-1]))
    always @(posedge clk) begin
        if (rst) begin
            hpf_x_prev <= 0;
            hpf_y_prev <= 0;
            pcm_out <= 0;
            pcm_valid <= 0;
        end else begin
            pcm_valid <= 0;
            
            if (cic_valid) begin
                if (hpf_alpha == 8'd255) begin
                    // Bypass HPF completely
                    pcm_out <= scaled_out;
                end else begin
                    // HPF computation: y[n] = alpha/256 * y[n-1] + (x[n] - x[n-1])
                    pcm_out <= hpf_calc;
                    hpf_x_prev <= scaled_out;
                    hpf_y_prev <= hpf_calc;
                end
                pcm_valid <= 1;
            end
        end
    end

endmodule
