module cic3_pdm (
    input  wire        clk,           // PDM clock
    input  wire        rst,           // active-high synchronous reset
    input  wire        pdm_in,        // 1-bit PDM data input

    input  wire [2:0]  scale_shift,   // Right shift amount (0-7 bits)
    input  wire [7:0]  dc_alpha,      // DC removal alpha (0=bypass, 255=strong removal)
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
    
    // DC removal filter registers
    reg signed [19:0] dc_accumulator;  // 20-bit to prevent overflow
    
    
    wire signed [CIC_WIDTH-1:0] pdm_signed = pdm_in ? 17'sd1 : -17'sd1;
    
    // CIC Integrator stages (run at PDM rate)
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            integrator1 <= 0;
            integrator2 <= 0;
        end else begin
            integrator1 <= integrator1 + pdm_signed;
            integrator2 <= integrator2 + integrator1;
        end
    end
    
    // Decimation counter and CIC comb stages
    always @(posedge clk or posedge rst) begin
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
            3'd2: scaled_out = {{1{cic_out[16]}}, cic_out[16:2]};
            3'd3: scaled_out = {{2{cic_out[16]}}, cic_out[16:3]};
            3'd4: scaled_out = {{3{cic_out[16]}}, cic_out[16:4]};
            3'd5: scaled_out = {{4{cic_out[16]}}, cic_out[16:5]};
            3'd6: scaled_out = {{5{cic_out[16]}}, cic_out[16:6]};
            3'd7: scaled_out = {{6{cic_out[16]}}, cic_out[16:7]};
        endcase
    end
    
    // DC removal filter - runs at decimated rate
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            dc_accumulator <= 20'sd0;
            pcm_out <= 0;
            pcm_valid <= 0;
        end else begin
            pcm_valid <= 0;
            
            if (cic_valid) begin
                if (dc_alpha == 8'd0) begin
                    // Bypass DC removal
                    pcm_out <= scaled_out;
                end else begin
                    // Simple leaky integrator with sign extension
                    case (dc_alpha)
                        8'd1:   dc_accumulator <= dc_accumulator - (dc_accumulator >>> 12) + {{4{scaled_out[15]}}, scaled_out};
                        8'd16:  dc_accumulator <= dc_accumulator - (dc_accumulator >>> 8) + {{4{scaled_out[15]}}, scaled_out};
                        8'd64:  dc_accumulator <= dc_accumulator - (dc_accumulator >>> 6) + {{4{scaled_out[15]}}, scaled_out};
                        8'd128:  dc_accumulator <= dc_accumulator - (dc_accumulator >>> 5) + {{4{scaled_out[15]}}, scaled_out};
                        8'd255: dc_accumulator <= dc_accumulator - (dc_accumulator >>> 4) + {{4{scaled_out[15]}}, scaled_out};
                        default: dc_accumulator <= dc_accumulator - (dc_accumulator >>> 8) + {{4{scaled_out[15]}}, scaled_out};
                    endcase
                    
                    // Output = input - DC estimate (using OLD estimate to avoid combinational loop)
                    pcm_out <= scaled_out - dc_accumulator[19:4];
                end
                pcm_valid <= 1;
            end
        end
    end
endmodule
